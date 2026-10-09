import 'dart:convert';

import 'package:drift/drift.dart';

import '../domain/inspection.dart';
import 'app_database.dart';

class InspectionRepository {
  const InspectionRepository(this.database);

  final AppDatabase database;

  Stream<List<StoredInspection>> watchAll() => database.watchInspections();
  Future<List<StoredInspection>> pending() => database.pendingInspections();

  Future<void> save(InspectionDraft draft, {AnalysisResult? result}) async {
    final geo = draft.geo;
    final imagePath = draft.imagePath;
    final capturedAt = draft.capturedAt;
    if (geo == null || imagePath == null || capturedAt == null) {
      throw StateError('Cannot save an incomplete inspection.');
    }
    await database.upsertInspection(
      InspectionRecordsCompanion.insert(
        id: draft.id,
        imagePath: imagePath,
        latitude: geo.latitude,
        longitude: geo.longitude,
        gpsAccuracy: geo.accuracy,
        locationName: Value(geo.locationName),
        capturedAt: capturedAt,
        damageType: Value(draft.damageType),
        confidence: Value(draft.confidence),
        severity: Value(draft.severity),
        analysisStatus: draft.analysisStatus,
        syncStatus: draft.syncStatus,
        resultJson: Value(
          result == null ? null : jsonEncode(_resultToJson(result)),
        ),
      ),
    );
  }

  Future<void> markForReporting(
    InspectionDraft draft,
    AnalysisResult? result,
  ) => save(draft.copyWith(syncStatus: 'report_pending'), result: result);

  static Map<String, dynamic> _resultToJson(AnalysisResult result) => {
    'detected': result.detected,
    'image': {'width': result.imageWidth, 'height': result.imageHeight},
    'severity': result.severity == null ? null : {'level': result.severity},
    'message': result.message,
    'detections': result.detections
        .map(
          (item) => {
            'damage_type': item.damageType,
            'confidence': item.confidence,
            'bbox': {
              'x1': item.bbox.x1,
              'y1': item.bbox.y1,
              'x2': item.bbox.x2,
              'y2': item.bbox.y2,
            },
          },
        )
        .toList(),
  };
}
