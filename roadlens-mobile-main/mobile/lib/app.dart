import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/app_theme.dart';
import 'features/inspection/application/providers.dart';
import 'features/inspection/presentation/splash_login.dart';

class RoadLensApp extends ConsumerStatefulWidget {
  const RoadLensApp({super.key});

  @override
  ConsumerState<RoadLensApp> createState() => _RoadLensAppState();
}

class _RoadLensAppState extends ConsumerState<RoadLensApp> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(syncServiceProvider).start();
    });
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'RoadLens',
    debugShowCheckedModeBanner: false,
    theme: AppTheme.light,
    home: const SplashScreen(),
  );
}
