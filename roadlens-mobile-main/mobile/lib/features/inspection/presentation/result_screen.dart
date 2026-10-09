import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../application/providers.dart';
import '../domain/inspection.dart';
import 'annotated_image.dart';
import 'camera_screen.dart';

class ResultScreen extends ConsumerWidget {
  const ResultScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(inspectionControllerProvider);
    final draft = state.draft;
    if (draft?.imagePath == null ||
        draft?.geo == null ||
        draft?.capturedAt == null) {
      return const Scaffold(
        body: Center(child: Text('Inspection result is unavailable.')),
      );
    }
    final result = state.result;
    final primary = result?.primary;
    final captured = DateTime.parse(draft!.capturedAt!).toLocal();
    return Scaffold(
      appBar: AppBar(title: const Text('Road inspection result')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          if (result != null)
            AnnotatedImage(imagePath: draft.imagePath!, result: result)
          else
            ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: Image.file(
                File(draft.imagePath!),
                height: 320,
                fit: BoxFit.contain,
              ),
            ),
          const SizedBox(height: 18),
          if (state.phase == InspectionPhase.offlinePending)
            const _StatusBanner(
              icon: Icons.cloud_off,
              color: Colors.orange,
              title: 'Analysis pending',
              message: 'The backend is unavailable. The image and metadata are saved locally and will retry when connectivity returns.',
            )
          else if (result?.detected == false)
            const _StatusBanner(
              icon: Icons.check_circle_outline,
              color: Colors.green,
              title: 'No supported road damage detected.',
              message: 'The inspection still retains its image, GPS, location, and timestamp.',
            )
          else
            _StatusBanner(
              icon: Icons.warning_amber_rounded,
              color: Colors.red,
              title: primary?.damageType ?? 'Road damage detected',
              message:
                  'Severity ${result?.severity ?? 'Not available'} • Confidence ${primary == null ? '—' : '${(primary.confidence * 100).toStringAsFixed(0)}%'}',
            ),
          const SizedBox(height: 12),
          _ResultRow(
            label: 'GPS',
            value:
                '${draft.geo!.latitude.toStringAsFixed(6)}, ${draft.geo!.longitude.toStringAsFixed(6)} (±${draft.geo!.accuracy.toStringAsFixed(1)} m)',
          ),
          _ResultRow(
            label: 'Location',
            value:
                draft.geo!.locationName ??
                'Address unavailable — coordinates retained',
          ),
          _ResultRow(
            label: 'Captured',
            value: DateFormat('d MMM y, h:mm a').format(captured),
          ),
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: () => ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(content: Text('Inspection is saved locally.')),
            ),
            icon: const Icon(Icons.save_outlined),
            label: const Text('SAVE INSPECTION'),
          ),
          if (result?.detected == true) ...[
            const SizedBox(height: 10),
            OutlinedButton.icon(
              onPressed: () async {
                await ref
                    .read(inspectionControllerProvider.notifier)
                    .markForReporting();
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Damage report queued.')),
                  );
                }
              },
              icon: const Icon(Icons.campaign_outlined),
              label: const Text('REPORT DAMAGE'),
            ),
          ],
          const SizedBox(height: 10),
          TextButton.icon(
            onPressed: () {
              unawaited(
                ref
                    .read(inspectionControllerProvider.notifier)
                    .startNewInspection(),
              );
              Navigator.of(context).pushReplacement(
                MaterialPageRoute<void>(builder: (_) => const CameraScreen()),
              );
            },
            icon: const Icon(Icons.camera_alt_outlined),
            label: const Text('NEW INSPECTION'),
          ),
        ],
      ),
    );
  }
}

class _StatusBanner extends StatelessWidget {
  const _StatusBanner({
    required this.icon,
    required this.color,
    required this.title,
    required this.message,
  });
  final IconData icon;
  final Color color;
  final String title;
  final String message;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 17,
                  ),
                ),
                const SizedBox(height: 4),
                Text(message),
              ],
            ),
          ),
        ],
      ),
    ),
  );
}

class _ResultRow extends StatelessWidget {
  const _ResultRow({required this.label, required this.value});
  final String label;
  final String value;
  @override
  Widget build(BuildContext context) => ListTile(
    contentPadding: EdgeInsets.zero,
    title: Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
    subtitle: Text(value),
  );
}
