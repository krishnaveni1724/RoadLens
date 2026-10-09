import 'package:flutter_test/flutter_test.dart';
import 'package:roadlens/features/inspection/domain/inspection.dart';

void main() {
  test('capture timestamp always includes a timezone offset', () {
    final timestamp = timezoneAwareIsoNow();
    expect(timestamp, matches(RegExp(r'[+-]\d{2}:\d{2}$')));
    expect(DateTime.tryParse(timestamp), isNotNull);
  });

  test('real API response maps detections and no-damage explicitly', () {
    final detected = AnalysisResult.fromJson({
      'detected': true,
      'image': {'width': 1448, 'height': 1086},
      'severity': {'level': 'HIGH'},
      'detections': [
        {
          'damage_type': 'Pothole',
          'confidence': 0.91,
          'bbox': {'x1': 105, 'y1': 160, 'x2': 430, 'y2': 410},
        },
      ],
    });
    expect(detected.detected, isTrue);
    expect(detected.primary?.damageType, 'Pothole');
    expect(detected.primary?.confidence, 0.91);
    expect(detected.severity, 'HIGH');

    final clean = AnalysisResult.fromJson({
      'detected': false,
      'image': {'width': 640, 'height': 480},
      'detections': <Object>[],
    });
    expect(clean.detected, isFalse);
    expect(clean.detections, isEmpty);
  });
}
