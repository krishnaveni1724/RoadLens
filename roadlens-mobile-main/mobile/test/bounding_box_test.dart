import 'dart:ui';

import 'package:flutter_test/flutter_test.dart';
import 'package:roadlens/features/inspection/domain/inspection.dart';
import 'package:roadlens/features/inspection/presentation/annotated_image.dart';

void main() {
  test('bounding box follows BoxFit.contain with centered letterboxing', () {
    const box = DetectionBox(x1: 100, y1: 50, x2: 300, y2: 150);
    final mapped = fittedDetectionRect(
      box,
      const Size(400, 200),
      const Size(400, 400),
    );
    expect(mapped, const Rect.fromLTRB(100, 150, 300, 250));
  });
}
