import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:path/path.dart' as path;
import 'package:path_provider/path_provider.dart';

part 'app_database.g.dart';

@DataClassName('StoredInspection')
class InspectionRecords extends Table {
  TextColumn get id => text()();
  TextColumn get imagePath => text()();
  RealColumn get latitude => real()();
  RealColumn get longitude => real()();
  RealColumn get gpsAccuracy => real()();
  TextColumn get locationName => text().nullable()();
  TextColumn get capturedAt => text()();
  TextColumn get damageType => text().nullable()();
  RealColumn get confidence => real().nullable()();
  TextColumn get severity => text().nullable()();
  TextColumn get analysisStatus => text()();
  TextColumn get syncStatus => text()();
  TextColumn get resultJson => text().nullable()();

  @override
  Set<Column<Object>> get primaryKey => {id};
}

@DriftDatabase(tables: [InspectionRecords])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  Stream<List<StoredInspection>> watchInspections() => (select(
    inspectionRecords,
  )..orderBy([(row) => OrderingTerm.desc(row.capturedAt)])).watch();

  Future<List<StoredInspection>> pendingInspections() => (select(
    inspectionRecords,
  )..where((row) => row.analysisStatus.equals('pending'))).get();

  Future<void> upsertInspection(InspectionRecordsCompanion record) =>
      into(inspectionRecords).insertOnConflictUpdate(record);
}

LazyDatabase _openConnection() => LazyDatabase(() async {
  final directory = await getApplicationDocumentsDirectory();
  return NativeDatabase.createInBackground(
    File(path.join(directory.path, 'roadlens.sqlite')),
  );
});
