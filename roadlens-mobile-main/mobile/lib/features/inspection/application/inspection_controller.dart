import 'dart:io';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../data/inspection_repository.dart';
import '../domain/inspection.dart';
import '../services/analysis_service.dart';
import '../services/camera_service.dart';
import '../services/geocoding_service.dart';
import '../services/location_service.dart';
import '../services/permission_service.dart';

const lowGpsAccuracyWarningMeters = 30.0;

class InspectionController extends StateNotifier<InspectionState> {
  InspectionController({
    required this._camera,
    required this._location,
    required this._geocoding,
    required this._permissions,
    required this._analysis,
    required this._repository,
  }) : super(const InspectionState());

  final RoadLensCameraService _camera;
  final RoadLensLocationService _location;
  final RoadLensGeocodingService _geocoding;
  final InspectionPermissionService _permissions;
  final RoadDamageAnalysisService _analysis;
  final InspectionRepository _repository;

  Future<void> startNewInspection() async {
    final draft = InspectionDraft(id: const Uuid().v4());
    state = InspectionState(
      phase: InspectionPhase.requestingPermissions,
      gpsStatus: GpsStatus.idle,
      draft: draft,
    );
    final permissionResult = await _permissions.ensureRequiredPermissions();
    if (state.draft?.id != draft.id) return;
    if (!permissionResult.allowed) {
      state = state.copyWith(
        phase: InspectionPhase.error,
        message: permissionResult.message,
        errorCode: 'permission_denied',
        cameraPermanentlyDenied: permissionResult.cameraPermanentlyDenied,
        locationPermanentlyDenied: permissionResult.locationPermanentlyDenied,
      );
      return;
    }

    if (!await _location.isEnabled()) {
      state = state.copyWith(
        phase: InspectionPhase.error,
        message: 'Location services are required for a road inspection.',
        errorCode: 'location_services_disabled',
        locationServicesDisabled: true,
      );
      return;
    }

    state = state.copyWith(
      phase: InspectionPhase.acquiringLocation,
      gpsStatus: GpsStatus.acquiring,
      clearMessage: true,
    );
    final locationFuture = _acquireLocation();
    try {
      await _camera.initializeRearCamera();
    } catch (error) {
      state = state.copyWith(
        phase: InspectionPhase.error,
        message: 'Unable to open the camera.',
        errorCode: 'camera_initialization_failed',
      );
      return;
    }
    if (state.draft?.id != draft.id) return;
    state = state.copyWith(phase: InspectionPhase.cameraReady);
    try {
      final geo = await locationFuture;
      if (state.draft?.id != draft.id) return;
      state = state.copyWith(
        phase: InspectionPhase.cameraReady,
        gpsStatus: GpsStatus.ready,
        draft: draft.copyWith(geo: geo),
        message: geo.accuracy > lowGpsAccuracyWarningMeters
            ? 'Low GPS accuracy'
            : null,
        clearMessage: geo.accuracy <= lowGpsAccuracyWarningMeters,
      );
    } catch (_) {
      if (state.draft?.id != draft.id) return;
      state = state.copyWith(
        phase: InspectionPhase.cameraReady,
        gpsStatus: GpsStatus.failed,
        message: 'Unable to obtain your location. Road inspections require GPS coordinates.',
        errorCode: 'location_unavailable',
      );
    }
  }

  Future<GeoSnapshot> _acquireLocation() async {
    final raw = await _location.currentPosition();
    final name = await _geocoding.reverse(raw.latitude, raw.longitude);
    return name == null ? raw : raw.copyWith(locationName: name);
  }

  Future<void> retryLocation() async {
    final draft = state.draft;
    if (draft == null) return;
    state = state.copyWith(gpsStatus: GpsStatus.acquiring, clearMessage: true);
    try {
      final geo = await _acquireLocation();
      if (state.draft?.id != draft.id) return;
      state = state.copyWith(
        gpsStatus: GpsStatus.ready,
        draft: draft.copyWith(geo: geo),
        message: geo.accuracy > lowGpsAccuracyWarningMeters
            ? 'Low GPS accuracy'
            : null,
        clearMessage: geo.accuracy <= lowGpsAccuracyWarningMeters,
      );
    } catch (_) {
      state = state.copyWith(
        gpsStatus: GpsStatus.failed,
        message: 'Unable to obtain your location. Road inspections require GPS coordinates.',
        errorCode: 'location_unavailable',
      );
    }
  }

  Future<void> capture() async {
    final draft = state.draft;
    if (draft == null ||
        draft.geo == null ||
        state.gpsStatus != GpsStatus.ready) {
      return;
    }
    state = state.copyWith(
      phase: InspectionPhase.capturing,
      clearMessage: true,
    );
    try {
      final imagePath = await _camera.captureValidatedImage();
      state = state.copyWith(
        phase: InspectionPhase.preview,
        draft: draft.copyWith(
          imagePath: imagePath,
          capturedAt: timezoneAwareIsoNow(),
        ),
      );
    } catch (error) {
      state = state.copyWith(
        phase: InspectionPhase.cameraReady,
        message: 'The captured image was invalid. Please try again.',
        errorCode: 'invalid_capture',
      );
    }
  }

  Future<void> retake() async {
    final draft = state.draft;
    final temporaryPath = draft?.imagePath;
    if (temporaryPath != null) {
      try {
        await File(temporaryPath).delete();
      } catch (_) {}
    }
    if (draft != null) {
      state = state.copyWith(
        phase: InspectionPhase.cameraReady,
        draft: draft.copyWith(clearImage: true, clearCapture: true),
        clearResult: true,
        clearMessage: true,
      );
    }
  }

  Future<void> usePhoto() async {
    var draft = state.draft;
    if (draft?.imagePath == null ||
        draft?.geo == null ||
        draft?.capturedAt == null) {
      state = state.copyWith(
        phase: InspectionPhase.error,
        message: 'Image, GPS, and timestamp are required before analysis.',
        errorCode: 'incomplete_inspection',
      );
      return;
    }
    final storedPath = await _camera.persistImage(draft!.imagePath!, draft.id);
    draft = draft.copyWith(
      imagePath: storedPath,
      analysisStatus: 'pending',
      syncStatus: 'pending',
    );
    state = state.copyWith(
      phase: InspectionPhase.analyzing,
      draft: draft,
      clearMessage: true,
    );
    await _repository.save(draft);
    try {
      final result = await _analysis.analyze(draft);
      final primary = result.primary;
      draft = draft.copyWith(
        damageType: primary?.damageType,
        confidence: primary?.confidence,
        severity: result.severity,
        analysisStatus: 'completed',
      );
      await _repository.save(draft, result: result);
      state = state.copyWith(
        phase: result.detected
            ? InspectionPhase.success
            : InspectionPhase.noDamage,
        draft: draft,
        result: result,
      );
    } catch (_) {
      draft = draft!.copyWith(analysisStatus: 'pending', syncStatus: 'pending');
      await _repository.save(draft);
      state = state.copyWith(
        phase: InspectionPhase.offlinePending,
        draft: draft,
        message: 'Backend unavailable. This inspection is saved and analysis is pending.',
        errorCode: 'backend_unavailable',
      );
    }
  }

  Future<void> toggleFlash() => _camera.toggleFlash();
  Future<bool> openAppSettings() => _permissions.openSettings();
  Future<bool> openLocationSettings() => _location.openSettings();
  Future<void> disposeCamera() => _camera.dispose();

  Future<void> markForReporting() async {
    final draft = state.draft;
    if (draft == null) return;
    final updated = draft.copyWith(syncStatus: 'report_pending');
    await _repository.markForReporting(updated, state.result);
    state = state.copyWith(
      draft: updated,
      message: 'Damage report queued for synchronization.',
    );
  }
}
