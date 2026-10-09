import 'dart:async';
import 'dart:io';

import 'package:connectivity_plus/connectivity_plus.dart';

import '../data/app_database.dart';
import '../data/inspection_repository.dart';
import '../domain/inspection.dart';
import '../services/analysis_service.dart';

class InspectionSyncService {
  InspectionSyncService(this._repository, this._analysis);

  final InspectionRepository _repository;
  final RoadDamageAnalysisService _analysis;
  StreamSubscription<List<ConnectivityResult>>? _subscription;
  bool _syncing = false;

  void start() {
    _subscription ??= Connectivity().onConnectivityChanged.listen((results) {
      if (results.any((result) => result != ConnectivityResult.none)) {
        unawaited(syncPending());
      }
    });
    unawaited(syncPending());
  }

  Future<void> syncPending() async {
    if (_syncing) return;
    _syncing = true;
    try {
      for (final stored in await _repository.pending()) {
        if (!await File(stored.imagePath).exists()) continue;
        final draft = _fromStored(stored);
        try {
          final result = await _analysis.analyze(draft);
          final primary = result.primary;
          await _repository.save(
            draft.copyWith(
              damageType: primary?.damageType,
              confidence: primary?.confidence,
              severity: result.severity,
              analysisStatus: 'completed',
            ),
            result: result,
          );
        } catch (_) {
          break;
        }
      }
    } finally {
      _syncing = false;
    }
  }

  InspectionDraft _fromStored(StoredInspection stored) => InspectionDraft(
    id: stored.id,
    imagePath: stored.imagePath,
    geo: GeoSnapshot(
      latitude: stored.latitude,
      longitude: stored.longitude,
      accuracy: stored.gpsAccuracy,
      locationName: stored.locationName,
    ),
    capturedAt: stored.capturedAt,
    damageType: stored.damageType,
    confidence: stored.confidence,
    severity: stored.severity,
    analysisStatus: stored.analysisStatus,
    syncStatus: stored.syncStatus,
  );

  void dispose() => _subscription?.cancel();
}
