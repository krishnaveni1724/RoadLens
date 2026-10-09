import 'dart:io';

import 'package:flutter/material.dart';

import '../domain/inspection.dart';

Rect fittedDetectionRect(DetectionBox box, Size imageSize, Size canvasSize) {
  final scale =
      (canvasSize.width / imageSize.width).clamp(0.0, double.infinity) <
          (canvasSize.height / imageSize.height).clamp(0.0, double.infinity)
      ? canvasSize.width / imageSize.width
      : canvasSize.height / imageSize.height;
  final rendered = Size(imageSize.width * scale, imageSize.height * scale);
  final offset = Offset(
    (canvasSize.width - rendered.width) / 2,
    (canvasSize.height - rendered.height) / 2,
  );
  return Rect.fromLTRB(
    offset.dx + box.x1 * scale,
    offset.dy + box.y1 * scale,
    offset.dx + box.x2 * scale,
    offset.dy + box.y2 * scale,
  );
}

class AnnotatedImage extends StatelessWidget {
  const AnnotatedImage({
    super.key,
    required this.imagePath,
    required this.result,
  });
  final String imagePath;
  final AnalysisResult result;

  @override
  Widget build(BuildContext context) => SizedBox(
    height: 320,
    child: ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: LayoutBuilder(
        builder: (context, constraints) {
          final size = Size(constraints.maxWidth, constraints.maxHeight);
          return Stack(
            fit: StackFit.expand,
            children: [
              ColoredBox(
                color: Colors.black,
                child: Image.file(File(imagePath), fit: BoxFit.contain),
              ),
              CustomPaint(
                painter: DetectionPainter(
                  result: result,
                  imageSize: Size(
                    result.imageWidth.toDouble(),
                    result.imageHeight.toDouble(),
                  ),
                  canvasSize: size,
                ),
              ),
            ],
          );
        },
      ),
    ),
  );
}

class DetectionPainter extends CustomPainter {
  const DetectionPainter({
    required this.result,
    required this.imageSize,
    required this.canvasSize,
  });
  final AnalysisResult result;
  final Size imageSize;
  final Size canvasSize;

  @override
  void paint(Canvas canvas, Size size) {
    final boxPaint = Paint()
      ..color = const Color(0xFFFFC043)
      ..style = PaintingStyle.stroke
      ..strokeWidth = 3;
    for (final detection in result.detections) {
      final rect = fittedDetectionRect(detection.bbox, imageSize, size);
      canvas.drawRect(rect, boxPaint);
      final label =
          '${detection.damageType} ${(detection.confidence * 100).toStringAsFixed(0)}%';
      final textPainter = TextPainter(
        text: TextSpan(
          text: label,
          style: const TextStyle(
            color: Colors.black,
            backgroundColor: Color(0xFFFFC043),
            fontWeight: FontWeight.bold,
            fontSize: 13,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();
      textPainter.paint(
        canvas,
        Offset(
          rect.left,
          (rect.top - textPainter.height).clamp(0, size.height),
        ),
      );
    }
  }

  @override
  bool shouldRepaint(covariant DetectionPainter oldDelegate) =>
      oldDelegate.result != result ||
      oldDelegate.imageSize != imageSize ||
      oldDelegate.canvasSize != canvasSize;
}
