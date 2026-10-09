import 'package:dio/dio.dart';

import '../domain/inspection.dart';

class RoadDamageAnalysisService {
  RoadDamageAnalysisService(String baseUrl)
    : _dio = Dio(
        BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 12),
          sendTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 90),
        ),
      );

  final Dio _dio;

  Future<AnalysisResult> analyze(InspectionDraft draft) async {
    final geo = draft.geo;
    final imagePath = draft.imagePath;
    final capturedAt = draft.capturedAt;
    if (geo == null || imagePath == null || capturedAt == null) {
      throw StateError('Image, GPS, and capture timestamp are required.');
    }
    final form = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        imagePath,
        filename: 'road-inspection.jpg',
      ),
      'latitude': geo.latitude.toString(),
      'longitude': geo.longitude.toString(),
      'gps_accuracy': geo.accuracy.toString(),
      'captured_at': capturedAt,
    });
    final response = await _dio.post<Map<String, dynamic>>(
      '/api/analyze',
      data: form,
    );
    final data = response.data;
    if (data == null || data['success'] != true) {
      throw StateError('The analysis service returned an invalid response.');
    }
    return AnalysisResult.fromJson(data);
  }
}
