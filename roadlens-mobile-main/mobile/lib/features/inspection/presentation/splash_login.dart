import 'dart:async';

import 'package:flutter/material.dart';

import 'home_shell.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    Timer(const Duration(milliseconds: 850), () {
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute<void>(builder: (_) => const LoginScreen()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) => const Scaffold(
    body: Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircleAvatar(
            radius: 38,
            backgroundColor: Color(0xFF1877F2),
            child: Icon(Icons.route_rounded, color: Colors.white, size: 40),
          ),
          SizedBox(height: 18),
          Text(
            'RoadLens',
            style: TextStyle(fontSize: 30, fontWeight: FontWeight.w800),
          ),
          SizedBox(height: 6),
          Text('AI road inspection operations'),
        ],
      ),
    ),
  );
}

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
    body: SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Spacer(),
            const Icon(
              Icons.shield_outlined,
              size: 58,
              color: Color(0xFF1877F2),
            ),
            const SizedBox(height: 20),
            Text(
              'RoadLens operator',
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineSmall
                  ?.copyWith(fontWeight: FontWeight.w800),
            ),
            const SizedBox(height: 10),
            const Text(
              'The current RoadLens backend has no authentication API. Continue in local inspection mode; no password is collected or stored.',
              textAlign: TextAlign.center,
            ),
            const Spacer(),
            FilledButton.icon(
              onPressed: () => Navigator.of(context).pushReplacement(
                MaterialPageRoute<void>(builder: (_) => const HomeShell()),
              ),
              icon: const Icon(Icons.arrow_forward_rounded),
              label: const Text('Continue to dashboard'),
            ),
          ],
        ),
      ),
    ),
  );
}
