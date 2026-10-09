import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../application/providers.dart';
import '../domain/inspection.dart';
import 'result_screen.dart';

class PreviewScreen extends ConsumerWidget {
  const PreviewScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(inspectionControllerProvider);
    final draft = state.draft;
    if (draft?.imagePath == null ||
        draft?.geo == null ||
        draft?.capturedAt == null) {
      return const Scaffold(
        body: Center(child: Text('Captured inspection data is incomplete.')),
      );
    }
    final analyzing =
        state.phase == InspectionPhase.analyzing ||
        state.phase == InspectionPhase.uploading;
    return Scaffold(
      appBar: AppBar(title: const Text('Photo preview')),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: Image.file(File(draft!.imagePath!), fit: BoxFit.contain),
          ),
          const SizedBox(height: 18),
          _MetaRow(
            icon: Icons.gps_fixed,
            label: 'GPS',
            value:
                '${draft.geo!.latitude.toStringAsFixed(6)}, ${draft.geo!.longitude.toStringAsFixed(6)} (±${draft.geo!.accuracy.toStringAsFixed(1)} m)',
          ),
          _MetaRow(
            icon: Icons.location_on_outlined,
            label: 'Location',
            value:
                draft.geo!.locationName ??
                'Address unavailable — coordinates retained',
          ),
          _MetaRow(
            icon: Icons.schedule,
            label: 'Timestamp',
            value: draft.capturedAt!,
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: analyzing
                      ? null
                      : () async {
                          await ref
                              .read(inspectionControllerProvider.notifier)
                              .retake();
                          if (context.mounted) Navigator.of(context).pop();
                        },
                  icon: const Icon(Icons.replay),
                  label: const Text('RETAKE'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: FilledButton.icon(
                  onPressed: analyzing
                      ? null
                      : () async {
                          await ref
                              .read(inspectionControllerProvider.notifier)
                              .usePhoto();
                          if (context.mounted) {
                            Navigator.of(context).pushReplacement(
                              MaterialPageRoute<void>(
                                builder: (_) => const ResultScreen(),
                              ),
                            );
                          }
                        },
                  icon: analyzing
                      ? const SizedBox.square(
                          dimension: 18,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.check),
                  label: Text(analyzing ? 'ANALYZING...' : 'USE PHOTO'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _MetaRow extends StatelessWidget {
  const _MetaRow({
    required this.icon,
    required this.label,
    required this.value,
  });
  final IconData icon;
  final String label;
  final String value;

  @override
  Widget build(BuildContext context) => Card(
    child: ListTile(
      leading: Icon(icon, color: Theme.of(context).colorScheme.primary),
      title: Text(label),
      subtitle: Text(value),
      trailing: const Icon(Icons.check_circle, color: Colors.green),
    ),
  );
}
