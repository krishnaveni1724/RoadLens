import 'dart:async';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../application/providers.dart';
import '../data/app_database.dart';
import 'camera_screen.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int index = 0;

  @override
  Widget build(BuildContext context) {
    const pages = [DashboardTab(), HistoryTab(), MapTab(), SettingsTab()];
    return Scaffold(
      body: SafeArea(
        child: IndexedStack(index: index, children: pages),
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        onDestinationSelected: (value) => setState(() => index = value),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.dashboard_outlined),
            selectedIcon: Icon(Icons.dashboard),
            label: 'Dashboard',
          ),
          NavigationDestination(icon: Icon(Icons.history), label: 'History'),
          NavigationDestination(
            icon: Icon(Icons.map_outlined),
            selectedIcon: Icon(Icons.map),
            label: 'Map',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
      ),
    );
  }
}

class DashboardTab extends ConsumerWidget {
  const DashboardTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final history =
        ref.watch(historyProvider).valueOrNull ?? const <StoredInspection>[];
    final pending = history
        .where((item) => item.analysisStatus == 'pending')
        .length;
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Row(
          children: [
            const CircleAvatar(child: Icon(Icons.route)),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                'RoadLens',
                style: Theme.of(context).textTheme.headlineSmall
                    ?.copyWith(fontWeight: FontWeight.w800),
              ),
            ),
            const Icon(Icons.cloud_done_outlined),
          ],
        ),
        const SizedBox(height: 26),
        Text(
          'Road inspection dashboard',
          style: Theme.of(context).textTheme.headlineMedium
              ?.copyWith(fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 8),
        const Text(
          'Capture road damage with verified GPS, timestamp, and real ONNX analysis.',
        ),
        const SizedBox(height: 24),
        FilledButton.icon(
          key: const Key('newInspectionButton'),
          onPressed: () {
            unawaited(
              ref
                  .read(inspectionControllerProvider.notifier)
                  .startNewInspection(),
            );
            Navigator.of(context).push(
              MaterialPageRoute<void>(builder: (_) => const CameraScreen()),
            );
          },
          icon: const Icon(Icons.camera_alt_rounded),
          label: const Text('NEW INSPECTION'),
        ),
        const SizedBox(height: 18),
        Row(
          children: [
            Expanded(
              child: _StatCard(
                label: 'Saved',
                value: '${history.length}',
                icon: Icons.inventory_2_outlined,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _StatCard(
                label: 'Pending AI',
                value: '$pending',
                icon: Icons.sync_problem_outlined,
              ),
            ),
          ],
        ),
        const SizedBox(height: 22),
        Text(
          'Recent inspections',
          style: Theme.of(context).textTheme.titleLarge
              ?.copyWith(fontWeight: FontWeight.w700),
        ),
        const SizedBox(height: 10),
        if (history.isEmpty)
          const Card(
            child: Padding(
              padding: EdgeInsets.all(22),
              child: Text('No inspections yet. Start with the camera above.'),
            ),
          )
        else
          ...history.take(3).map((item) => _InspectionTile(item: item)),
      ],
    );
  }
}

class _StatCard extends StatelessWidget {
  const _StatCard({
    required this.label,
    required this.value,
    required this.icon,
  });
  final String label;
  final String value;
  final IconData icon;

  @override
  Widget build(BuildContext context) => Card(
    child: Padding(
      padding: const EdgeInsets.all(18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: Theme.of(context).colorScheme.primary),
          const SizedBox(height: 14),
          Text(
            value,
            style: Theme.of(context).textTheme.headlineMedium
                ?.copyWith(fontWeight: FontWeight.w800),
          ),
          Text(label),
        ],
      ),
    ),
  );
}

class HistoryTab extends ConsumerWidget {
  const HistoryTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) => ref
      .watch(historyProvider)
      .when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) =>
            Center(child: Text('Unable to load history: $error')),
        data: (items) => ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Text(
              'Inspection history',
              style: Theme.of(context).textTheme.headlineMedium
                  ?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 16),
            if (items.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(22),
                  child: Text(
                    'Saved inspections appear here, including offline pending items.',
                  ),
                ),
              ),
            ...items.map((item) => _InspectionTile(item: item)),
          ],
        ),
      );
}

class _InspectionTile extends StatelessWidget {
  const _InspectionTile({required this.item});
  final StoredInspection item;

  @override
  Widget build(BuildContext context) {
    final captured = DateTime.tryParse(item.capturedAt)?.toLocal();
    return Card(
      child: ListTile(
        contentPadding: const EdgeInsets.all(12),
        leading: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: SizedBox(
            width: 58,
            height: 58,
            child: Image.file(
              File(item.imagePath),
              fit: BoxFit.cover,
              errorBuilder: (_, _, _) =>
                  const Icon(Icons.broken_image_outlined),
            ),
          ),
        ),
        title: Text(
          item.damageType ??
              (item.analysisStatus == 'pending'
                  ? 'Analysis pending'
                  : 'No supported damage'),
        ),
        subtitle: Text(
          '${item.latitude.toStringAsFixed(5)}, ${item.longitude.toStringAsFixed(5)}\n${captured == null ? item.capturedAt : DateFormat('d MMM y, h:mm a').format(captured)}',
        ),
        isThreeLine: true,
        trailing: Icon(
          item.analysisStatus == 'pending'
              ? Icons.cloud_upload_outlined
              : Icons.check_circle,
          color: item.analysisStatus == 'pending'
              ? Colors.orange
              : Colors.green,
        ),
      ),
    );
  }
}

class MapTab extends ConsumerWidget {
  const MapTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final items =
        ref.watch(historyProvider).valueOrNull ?? const <StoredInspection>[];
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          'Inspection map',
          style: Theme.of(context).textTheme.headlineMedium
              ?.copyWith(fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 8),
        const Text(
          'Offline coordinate index. Coordinates remain the source of truth; no map tiles are required.',
        ),
        const SizedBox(height: 18),
        Container(
          height: 220,
          decoration: BoxDecoration(
            color: const Color(0xFFEAF2FF),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Stack(
            children: [
              const Positioned.fill(
                child: CustomPaint(painter: _MapGridPainter()),
              ),
              ...items
                  .take(20)
                  .map(
                    (item) => Positioned(
                      left:
                          ((item.longitude + 180) / 360) *
                          (MediaQuery.sizeOf(context).width - 72),
                      top: ((90 - item.latitude) / 180) * 190,
                      child: const Icon(
                        Icons.location_on,
                        color: Colors.red,
                        size: 22,
                      ),
                    ),
                  ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        ...items.map(
          (item) => ListTile(
            leading: const Icon(Icons.location_on_outlined),
            title: Text(item.locationName ?? 'Address unavailable'),
            subtitle: Text(
              '${item.latitude.toStringAsFixed(6)}, ${item.longitude.toStringAsFixed(6)}',
            ),
          ),
        ),
      ],
    );
  }
}

class _MapGridPainter extends CustomPainter {
  const _MapGridPainter();
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFFB8CDF0)
      ..strokeWidth = 1;
    for (var i = 1; i < 6; i++) {
      canvas.drawLine(
        Offset(size.width * i / 6, 0),
        Offset(size.width * i / 6, size.height),
        paint,
      );
      canvas.drawLine(
        Offset(0, size.height * i / 6),
        Offset(size.width, size.height * i / 6),
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

class SettingsTab extends ConsumerWidget {
  const SettingsTab({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final config = ref.watch(appConfigProvider);
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        Text(
          'Settings',
          style: Theme.of(context).textTheme.headlineMedium
              ?.copyWith(fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 18),
        Card(
          child: ListTile(
            leading: const Icon(Icons.hub_outlined),
            title: const Text('Environment'),
            subtitle: Text(config.environment),
          ),
        ),
        Card(
          child: ListTile(
            leading: const Icon(Icons.api_outlined),
            title: const Text('Analysis API'),
            subtitle: Text(config.apiBaseUrl),
          ),
        ),
        Card(
          child: ListTile(
            leading: const Icon(Icons.lock_outline),
            title: const Text('Production transport'),
            subtitle: const Text(
              'Production builds reject non-HTTPS API configuration.',
            ),
          ),
        ),
        const SizedBox(height: 16),
        OutlinedButton.icon(
          onPressed: () async {
            await ref.read(syncServiceProvider).syncPending();
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Pending analysis sync attempted.'),
                ),
              );
            }
          },
          icon: const Icon(Icons.sync),
          label: const Text('Retry pending analyses'),
        ),
      ],
    );
  }
}
