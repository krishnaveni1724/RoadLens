import 'package:intl/intl.dart';

enum InspectionPhase {
  idle,
  requestingPermissions,
  acquiringLocation,
  cameraReady,
  capturing,
  preview,
  uploading,
  analyzing,
  success,
  noDamage,
  offlinePending,
  error,
}

enum GpsStatus { idle, acquiring, ready, failed }

class GeoSnapshot {
  const GeoSnapshot({
    required this.latitude,
    required this.longitude,
    required this.accuracy,
    this.locationName,
  });

  final double latitude;
  final double longitude;
  final double accuracy;
  final String? locationName;

  GeoSnapshot copyWith({String? locationName}) => GeoSnapshot(
    latitude: latitude,
    longitude: longitude,
    accuracy: accuracy,
    locationName: locationName ?? this.locationName,
  );
}

class DetectionBox {
  const DetectionBox({
    required this.x1,
    required this.y1,
    required this.x2,
    required this.y2,
  });

  factory DetectionBox.fromJson(Map<String, dynamic> json) => DetectionBox(
    x1: (json['x1'] as num).toDouble(),
    y1: (json['y1'] as num).toDouble(),
    x2: (json['x2'] as num).toDouble(),
    y2: (json['y2'] as num).toDouble(),
  );

  final double x1;
  final double y1;
  final double x2;
  final double y2;
}

class DamageDetection {
  const DamageDetection({
    required this.damageType,
    required this.confidence,
    required this.bbox,
  });

  factory DamageDetection.fromJson(Map<String, dynamic> json) =>
      DamageDetection(
        damageType: (json['damage_type'] ?? json['damageType']) as String,
        confidence: (json['confidence'] as num).toDouble(),
        bbox: DetectionBox.fromJson(json['bbox'] as Map<String, dynamic>),
      );

  final String damageType;
  final double confidence;
  final DetectionBox bbox;
}

class AnalysisResult {
  const AnalysisResult({
    required this.detected,
    required this.detections,
    required this.imageWidth,
    required this.imageHeight,
    this.severity,
    this.message,
  });

  factory AnalysisResult.fromJson(Map<String, dynamic> json) {
    final image = json['image'] as Map<String, dynamic>? ?? const {};
    final severityJson = json['severity'] as Map<String, dynamic>?;
    return AnalysisResult(
      detected: json['detected'] as bool? ?? false,
      detections: (json['detections'] as List<dynamic>? ?? const [])
          .map((item) => DamageDetection.fromJson(item as Map<String, dynamic>))
          .toList(growable: false),
      imageWidth: (image['width'] as num?)?.toInt() ?? 1,
      imageHeight: (image['height'] as num?)?.toInt() ?? 1,
      severity: severityJson?['level'] as String?,
      message: json['message'] as String?,
    );
  }

  final bool detected;
  final List<DamageDetection> detections;
  final int imageWidth;
  final int imageHeight;
  final String? severity;
  final String? message;

  DamageDetection? get primary => detections.isEmpty ? null : detections.first;
}

class InspectionDraft {
  const InspectionDraft({
    required this.id,
    this.imagePath,
    this.geo,
    this.capturedAt,
    this.damageType,
    this.confidence,
    this.severity,
    this.analysisStatus = 'pending',
    this.syncStatus = 'pending',
  });

  final String id;
  final String? imagePath;
  final GeoSnapshot? geo;
  final String? capturedAt;
  final String? damageType;
  final double? confidence;
  final String? severity;
  final String analysisStatus;
  final String syncStatus;

  InspectionDraft copyWith({
    String? imagePath,
    bool clearImage = false,
    GeoSnapshot? geo,
    String? capturedAt,
    bool clearCapture = false,
    String? damageType,
    double? confidence,
    String? severity,
    String? analysisStatus,
    String? syncStatus,
  }) => InspectionDraft(
    id: id,
    imagePath: clearImage ? null : imagePath ?? this.imagePath,
    geo: geo ?? this.geo,
    capturedAt: clearCapture ? null : capturedAt ?? this.capturedAt,
    damageType: damageType ?? this.damageType,
    confidence: confidence ?? this.confidence,
    severity: severity ?? this.severity,
    analysisStatus: analysisStatus ?? this.analysisStatus,
    syncStatus: syncStatus ?? this.syncStatus,
  );
}

class InspectionState {
  const InspectionState({
    this.phase = InspectionPhase.idle,
    this.gpsStatus = GpsStatus.idle,
    this.draft,
    this.result,
    this.message,
    this.errorCode,
    this.cameraPermanentlyDenied = false,
    this.locationPermanentlyDenied = false,
    this.locationServicesDisabled = false,
  });

  final InspectionPhase phase;
  final GpsStatus gpsStatus;
  final InspectionDraft? draft;
  final AnalysisResult? result;
  final String? message;
  final String? errorCode;
  final bool cameraPermanentlyDenied;
  final bool locationPermanentlyDenied;
  final bool locationServicesDisabled;

  InspectionState copyWith({
    InspectionPhase? phase,
    GpsStatus? gpsStatus,
    InspectionDraft? draft,
    AnalysisResult? result,
    bool clearResult = false,
    String? message,
    bool clearMessage = false,
    String? errorCode,
    bool cameraPermanentlyDenied = false,
    bool locationPermanentlyDenied = false,
    bool locationServicesDisabled = false,
  }) => InspectionState(
    phase: phase ?? this.phase,
    gpsStatus: gpsStatus ?? this.gpsStatus,
    draft: draft ?? this.draft,
    result: clearResult ? null : result ?? this.result,
    message: clearMessage ? null : message ?? this.message,
    errorCode: errorCode,
    cameraPermanentlyDenied: cameraPermanentlyDenied,
    locationPermanentlyDenied: locationPermanentlyDenied,
    locationServicesDisabled: locationServicesDisabled,
  );
}

String timezoneAwareIsoNow() {
  final now = DateTime.now();
  final offset = now.timeZoneOffset;
  final sign = offset.isNegative ? '-' : '+';
  final absolute = offset.abs();
  final zone =
      '$sign${absolute.inHours.toString().padLeft(2, '0')}:'
      '${(absolute.inMinutes % 60).toString().padLeft(2, '0')}';
  return '${DateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS").format(now)}$zone';
}
