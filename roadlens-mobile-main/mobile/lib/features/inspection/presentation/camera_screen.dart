import 'dart:async';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../application/providers.dart';
import '../domain/inspection.dart';
import 'preview_screen.dart';

class CameraScreen extends ConsumerStatefulWidget {
  const CameraScreen({super.key});

  @override
  ConsumerState<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends ConsumerState<CameraScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (ref.read(inspectionControllerProvider).phase ==
          InspectionPhase.idle) {
        unawaited(
          ref.read(inspectionControllerProvider.notifier).startNewInspection(),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(inspectionControllerProvider);
    final cameraService = ref.watch(cameraServiceProvider);
    final camera = cameraService.controller;
    return PopScope(
      onPopInvokedWithResult: (didPop, _) {
        if (didPop) {
          unawaited(
            ref.read(inspectionControllerProvider.notifier).disposeCamera(),
          );
        }
      },
      child: Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(
          backgroundColor: Colors.black,
          foregroundColor: Colors.white,
          title: const Text('New inspection'),
          actions: [
            if (camera != null && camera.value.isInitialized)
              IconButton(
                tooltip: 'Flash',
                onPressed: () async {
                  try {
                    await ref
                        .read(inspectionControllerProvider.notifier)
                        .toggleFlash();
                    if (mounted) setState(() {});
                  } catch (_) {
                    if (!context.mounted) return;
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                          'Flash is not supported by this camera.',
                        ),
                      ),
                    );
                  }
                },
                icon: Icon(
                  cameraService.flashEnabled ? Icons.flash_on : Icons.flash_off,
                ),
              ),
          ],
        ),
        body: _body(state, camera),
      ),
    );
  }

  Widget _body(InspectionState state, CameraController? camera) {
    if (state.phase == InspectionPhase.error) return _errorState(state);
    if (camera == null || !camera.value.isInitialized) {
      final label = state.phase == InspectionPhase.requestingPermissions
          ? 'Requesting camera and location permissions...'
          : 'Opening rear camera...';
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 16),
            Text(label, style: const TextStyle(color: Colors.white)),
          ],
        ),
      );
    }
    final gpsReady =
        state.gpsStatus == GpsStatus.ready && state.draft?.geo != null;
    return Column(
      children: [
        Expanded(
          child: Stack(
            fit: StackFit.expand,
            children: [
              Center(child: CameraPreview(camera)),
              Positioned(
                left: 18,
                right: 18,
                top: 18,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 14,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.68),
                    borderRadius: BorderRadius.circular(14),
                  ),
                  child: const Text(
                    'Capture the pothole or road damage clearly.\nKeep the damaged area visible and avoid blurry photos.',
                    style: TextStyle(color: Colors.white),
                  ),
                ),
              ),
            ],
          ),
        ),
        Container(
          color: const Color(0xFF101418),
          padding: const EdgeInsets.fromLTRB(20, 14, 20, 24),
          child: Column(
            children: [
              Row(
                children: [
                  Icon(
                    gpsReady ? Icons.gps_fixed : Icons.gps_not_fixed,
                    color: gpsReady ? Colors.greenAccent : Colors.amber,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _gpsLabel(state),
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                  if (state.gpsStatus == GpsStatus.failed ||
                      state.message == 'Low GPS accuracy')
                    TextButton(
                      onPressed: ref
                          .read(inspectionControllerProvider.notifier)
                          .retryLocation,
                      child: const Text('Retry location'),
                    ),
                ],
              ),
              if (state.message != null)
                Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    state.message!,
                    style: const TextStyle(color: Colors.amber),
                  ),
                ),
              const SizedBox(height: 12),
              Semantics(
                button: true,
                label: 'Capture road image',
                child: GestureDetector(
                  onTap: gpsReady && state.phase == InspectionPhase.cameraReady
                      ? () async {
                          await ref
                              .read(inspectionControllerProvider.notifier)
                              .capture();
                          if (mounted &&
                              ref.read(inspectionControllerProvider).phase ==
                                  InspectionPhase.preview) {
                            await Navigator.of(context).push(
                              MaterialPageRoute<void>(
                                builder: (_) => const PreviewScreen(),
                              ),
                            );
                          }
                        }
                      : null,
                  child: Container(
                    width: 74,
                    height: 74,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: gpsReady ? Colors.white : Colors.white38,
                      border: Border.all(
                        color: const Color(0xFF1877F2),
                        width: 6,
                      ),
                    ),
                    child: state.phase == InspectionPhase.capturing
                        ? const Padding(
                            padding: EdgeInsets.all(18),
                            child: CircularProgressIndicator(),
                          )
                        : null,
                  ),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _gpsLabel(InspectionState state) {
    final geo = state.draft?.geo;
    return switch (state.gpsStatus) {
      GpsStatus.acquiring => 'GPS: Acquiring...',
      GpsStatus.ready when geo != null =>
        'GPS Ready • ${geo.latitude.toStringAsFixed(5)}, ${geo.longitude.toStringAsFixed(5)} • ±${geo.accuracy.toStringAsFixed(1)} m',
      GpsStatus.failed => 'GPS unavailable',
      _ => 'GPS: Waiting...',
    };
  }

  Widget _errorState(InspectionState state) => Padding(
    padding: const EdgeInsets.all(24),
    child: Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.error_outline, color: Colors.amber, size: 56),
          const SizedBox(height: 16),
          Text(
            state.message ?? 'Unable to start inspection.',
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.white, fontSize: 18),
          ),
          const SizedBox(height: 20),
          if (state.cameraPermanentlyDenied || state.locationPermanentlyDenied)
            FilledButton(
              onPressed: ref
                  .read(inspectionControllerProvider.notifier)
                  .openAppSettings,
              child: const Text('Open App Settings'),
            )
          else if (state.locationServicesDisabled)
            FilledButton(
              onPressed: ref
                  .read(inspectionControllerProvider.notifier)
                  .openLocationSettings,
              child: const Text('Open Location Settings'),
            ),
          const SizedBox(height: 10),
          OutlinedButton(
            onPressed: ref
                .read(inspectionControllerProvider.notifier)
                .startNewInspection,
            child: const Text('Retry'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
        ],
      ),
    ),
  );
}
