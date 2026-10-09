import 'dart:io';
import 'dart:ui' as ui;

import 'package:camera/camera.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

class RoadLensCameraService {
  CameraController? _controller;
  bool _flashEnabled = false;

  CameraController? get controller => _controller;
  bool get isReady => _controller?.value.isInitialized ?? false;
  bool get flashEnabled => _flashEnabled;

  Future<void> initializeRearCamera() async {
    await dispose();
    final cameras = await availableCameras();
    if (cameras.isEmpty) {
      throw StateError('No camera is available on this device.');
    }
    final camera = cameras.firstWhere(
      (item) => item.lensDirection == CameraLensDirection.back,
      orElse: () => cameras.first,
    );
    final next = CameraController(
      camera,
      ResolutionPreset.high,
      enableAudio: false,
      imageFormatGroup: ImageFormatGroup.jpeg,
    );
    await next.initialize();
    _controller = next;
    _flashEnabled = false;
  }

  Future<void> toggleFlash() async {
    final camera = _controller;
    if (camera == null || !camera.value.isInitialized) return;
    _flashEnabled = !_flashEnabled;
    try {
      await camera.setFlashMode(
        _flashEnabled ? FlashMode.torch : FlashMode.off,
      );
    } on CameraException {
      _flashEnabled = false;
      await camera.setFlashMode(FlashMode.off);
      rethrow;
    }
  }

  Future<String> captureValidatedImage() async {
    final camera = _controller;
    if (camera == null || !camera.value.isInitialized) {
      throw StateError('Camera is not initialized.');
    }
    final capture = await camera.takePicture();
    final file = File(capture.path);
    if (!await file.exists() || await file.length() <= 0) {
      throw StateError('The camera returned an empty image.');
    }
    final bytes = await file.readAsBytes();
    final codec = await ui.instantiateImageCodec(bytes);
    final frame = await codec.getNextFrame();
    frame.image.dispose();
    codec.dispose();
    return file.path;
  }

  Future<String> persistImage(String sourcePath, String inspectionId) async {
    final root = await getApplicationDocumentsDirectory();
    final directory = Directory(path.join(root.path, 'inspections'));
    await directory.create(recursive: true);
    final extension = path.extension(sourcePath).isEmpty
        ? '.jpg'
        : path.extension(sourcePath);
    final destination = path.join(directory.path, '$inspectionId$extension');
    return (await File(sourcePath).copy(destination)).path;
  }

  Future<void> dispose() async {
    final camera = _controller;
    _controller = null;
    if (camera != null) await camera.dispose();
  }
}
