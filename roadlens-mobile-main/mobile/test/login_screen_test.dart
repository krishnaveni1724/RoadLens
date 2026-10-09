import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:roadlens/features/inspection/presentation/splash_login.dart';

void main() {
  testWidgets('login is transparent about local mode', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: LoginScreen()));
    expect(find.text('RoadLens operator'), findsOneWidget);
    expect(find.textContaining('no authentication API'), findsOneWidget);
    expect(find.text('Continue to dashboard'), findsOneWidget);
  });
}
