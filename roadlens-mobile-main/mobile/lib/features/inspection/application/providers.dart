import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/app_config.dart';
import '../data/app_database.dart';
import '../data/inspection_repository.dart';
import '../domain/inspection.dart';
import '../services/analysis_service.dart';
import '../services/camera_service.dart';
import '../services/geocoding_service.dart';
import '../services/location_service.dart';
import '../services/permission_service.dart';
import 'inspection_controller.dart';
import 'sync_service.dart';

final appConfigProvider = Provider<AppConfig>(
  (ref) => AppConfig.fromEnvironment(),
);
final databaseProvider = Provider<AppDatabase>((ref) {
  final database = AppDatabase();
  ref.onDispose(database.close);
  return database;
});
final repositoryProvider = Provider<InspectionRepository>(
  (ref) => InspectionRepository(ref.watch(databaseProvider)),
);
final historyProvider = StreamProvider<List<StoredInspection>>(
  (ref) => ref.watch(repositoryProvider).watchAll(),
);
final cameraServiceProvider = Provider<RoadLensCameraService>((ref) {
  final service = RoadLensCameraService();
  ref.onDispose(service.dispose);
  return service;
});
final locationServiceProvider = Provider((ref) => RoadLensLocationService());
final geocodingServiceProvider = Provider((ref) => RoadLensGeocodingService());
final permissionServiceProvider = Provider(
  (ref) => InspectionPermissionService(),
);
final analysisServiceProvider = Provider(
  (ref) => RoadDamageAnalysisService(ref.watch(appConfigProvider).apiBaseUrl),
);
final inspectionControllerProvider =
    StateNotifierProvider<InspectionController, InspectionState>((ref) {
      return InspectionController(
        camera: ref.watch(cameraServiceProvider),
        location: ref.watch(locationServiceProvider),
        geocoding: ref.watch(geocodingServiceProvider),
        permissions: ref.watch(permissionServiceProvider),
        analysis: ref.watch(analysisServiceProvider),
        repository: ref.watch(repositoryProvider),
      );
    });
final syncServiceProvider = Provider<InspectionSyncService>((ref) {
  final service = InspectionSyncService(
    ref.watch(repositoryProvider),
    ref.watch(analysisServiceProvider),
  );
  ref.onDispose(service.dispose);
  return service;
});
