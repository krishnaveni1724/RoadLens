// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'app_database.dart';

// ignore_for_file: type=lint
class $InspectionRecordsTable extends InspectionRecords
    with TableInfo<$InspectionRecordsTable, StoredInspection> {
  @override
  final GeneratedDatabase attachedDatabase;
  final String? _alias;
  $InspectionRecordsTable(this.attachedDatabase, [this._alias]);
  static const VerificationMeta _idMeta = const VerificationMeta('id');
  @override
  late final GeneratedColumn<String> id = GeneratedColumn<String>(
    'id',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _imagePathMeta = const VerificationMeta(
    'imagePath',
  );
  @override
  late final GeneratedColumn<String> imagePath = GeneratedColumn<String>(
    'image_path',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _latitudeMeta = const VerificationMeta(
    'latitude',
  );
  @override
  late final GeneratedColumn<double> latitude = GeneratedColumn<double>(
    'latitude',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _longitudeMeta = const VerificationMeta(
    'longitude',
  );
  @override
  late final GeneratedColumn<double> longitude = GeneratedColumn<double>(
    'longitude',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _gpsAccuracyMeta = const VerificationMeta(
    'gpsAccuracy',
  );
  @override
  late final GeneratedColumn<double> gpsAccuracy = GeneratedColumn<double>(
    'gps_accuracy',
    aliasedName,
    false,
    type: DriftSqlType.double,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _locationNameMeta = const VerificationMeta(
    'locationName',
  );
  @override
  late final GeneratedColumn<String> locationName = GeneratedColumn<String>(
    'location_name',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _capturedAtMeta = const VerificationMeta(
    'capturedAt',
  );
  @override
  late final GeneratedColumn<String> capturedAt = GeneratedColumn<String>(
    'captured_at',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _damageTypeMeta = const VerificationMeta(
    'damageType',
  );
  @override
  late final GeneratedColumn<String> damageType = GeneratedColumn<String>(
    'damage_type',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _confidenceMeta = const VerificationMeta(
    'confidence',
  );
  @override
  late final GeneratedColumn<double> confidence = GeneratedColumn<double>(
    'confidence',
    aliasedName,
    true,
    type: DriftSqlType.double,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _severityMeta = const VerificationMeta(
    'severity',
  );
  @override
  late final GeneratedColumn<String> severity = GeneratedColumn<String>(
    'severity',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  static const VerificationMeta _analysisStatusMeta = const VerificationMeta(
    'analysisStatus',
  );
  @override
  late final GeneratedColumn<String> analysisStatus = GeneratedColumn<String>(
    'analysis_status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _syncStatusMeta = const VerificationMeta(
    'syncStatus',
  );
  @override
  late final GeneratedColumn<String> syncStatus = GeneratedColumn<String>(
    'sync_status',
    aliasedName,
    false,
    type: DriftSqlType.string,
    requiredDuringInsert: true,
  );
  static const VerificationMeta _resultJsonMeta = const VerificationMeta(
    'resultJson',
  );
  @override
  late final GeneratedColumn<String> resultJson = GeneratedColumn<String>(
    'result_json',
    aliasedName,
    true,
    type: DriftSqlType.string,
    requiredDuringInsert: false,
  );
  @override
  List<GeneratedColumn> get $columns => [
    id,
    imagePath,
    latitude,
    longitude,
    gpsAccuracy,
    locationName,
    capturedAt,
    damageType,
    confidence,
    severity,
    analysisStatus,
    syncStatus,
    resultJson,
  ];
  @override
  String get aliasedName => _alias ?? actualTableName;
  @override
  String get actualTableName => $name;
  static const String $name = 'inspection_records';
  @override
  VerificationContext validateIntegrity(
    Insertable<StoredInspection> instance, {
    bool isInserting = false,
  }) {
    final context = VerificationContext();
    final data = instance.toColumns(true);
    if (data.containsKey('id')) {
      context.handle(_idMeta, id.isAcceptableOrUnknown(data['id']!, _idMeta));
    } else if (isInserting) {
      context.missing(_idMeta);
    }
    if (data.containsKey('image_path')) {
      context.handle(
        _imagePathMeta,
        imagePath.isAcceptableOrUnknown(data['image_path']!, _imagePathMeta),
      );
    } else if (isInserting) {
      context.missing(_imagePathMeta);
    }
    if (data.containsKey('latitude')) {
      context.handle(
        _latitudeMeta,
        latitude.isAcceptableOrUnknown(data['latitude']!, _latitudeMeta),
      );
    } else if (isInserting) {
      context.missing(_latitudeMeta);
    }
    if (data.containsKey('longitude')) {
      context.handle(
        _longitudeMeta,
        longitude.isAcceptableOrUnknown(data['longitude']!, _longitudeMeta),
      );
    } else if (isInserting) {
      context.missing(_longitudeMeta);
    }
    if (data.containsKey('gps_accuracy')) {
      context.handle(
        _gpsAccuracyMeta,
        gpsAccuracy.isAcceptableOrUnknown(
          data['gps_accuracy']!,
          _gpsAccuracyMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_gpsAccuracyMeta);
    }
    if (data.containsKey('location_name')) {
      context.handle(
        _locationNameMeta,
        locationName.isAcceptableOrUnknown(
          data['location_name']!,
          _locationNameMeta,
        ),
      );
    }
    if (data.containsKey('captured_at')) {
      context.handle(
        _capturedAtMeta,
        capturedAt.isAcceptableOrUnknown(data['captured_at']!, _capturedAtMeta),
      );
    } else if (isInserting) {
      context.missing(_capturedAtMeta);
    }
    if (data.containsKey('damage_type')) {
      context.handle(
        _damageTypeMeta,
        damageType.isAcceptableOrUnknown(data['damage_type']!, _damageTypeMeta),
      );
    }
    if (data.containsKey('confidence')) {
      context.handle(
        _confidenceMeta,
        confidence.isAcceptableOrUnknown(data['confidence']!, _confidenceMeta),
      );
    }
    if (data.containsKey('severity')) {
      context.handle(
        _severityMeta,
        severity.isAcceptableOrUnknown(data['severity']!, _severityMeta),
      );
    }
    if (data.containsKey('analysis_status')) {
      context.handle(
        _analysisStatusMeta,
        analysisStatus.isAcceptableOrUnknown(
          data['analysis_status']!,
          _analysisStatusMeta,
        ),
      );
    } else if (isInserting) {
      context.missing(_analysisStatusMeta);
    }
    if (data.containsKey('sync_status')) {
      context.handle(
        _syncStatusMeta,
        syncStatus.isAcceptableOrUnknown(data['sync_status']!, _syncStatusMeta),
      );
    } else if (isInserting) {
      context.missing(_syncStatusMeta);
    }
    if (data.containsKey('result_json')) {
      context.handle(
        _resultJsonMeta,
        resultJson.isAcceptableOrUnknown(data['result_json']!, _resultJsonMeta),
      );
    }
    return context;
  }

  @override
  Set<GeneratedColumn> get $primaryKey => {id};
  @override
  StoredInspection map(Map<String, dynamic> data, {String? tablePrefix}) {
    final effectivePrefix = tablePrefix != null ? '$tablePrefix.' : '';
    return StoredInspection(
      id: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}id'],
      )!,
      imagePath: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}image_path'],
      )!,
      latitude: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}latitude'],
      )!,
      longitude: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}longitude'],
      )!,
      gpsAccuracy: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}gps_accuracy'],
      )!,
      locationName: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}location_name'],
      ),
      capturedAt: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}captured_at'],
      )!,
      damageType: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}damage_type'],
      ),
      confidence: attachedDatabase.typeMapping.read(
        DriftSqlType.double,
        data['${effectivePrefix}confidence'],
      ),
      severity: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}severity'],
      ),
      analysisStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}analysis_status'],
      )!,
      syncStatus: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}sync_status'],
      )!,
      resultJson: attachedDatabase.typeMapping.read(
        DriftSqlType.string,
        data['${effectivePrefix}result_json'],
      ),
    );
  }

  @override
  $InspectionRecordsTable createAlias(String alias) {
    return $InspectionRecordsTable(attachedDatabase, alias);
  }
}

class StoredInspection extends DataClass
    implements Insertable<StoredInspection> {
  final String id;
  final String imagePath;
  final double latitude;
  final double longitude;
  final double gpsAccuracy;
  final String? locationName;
  final String capturedAt;
  final String? damageType;
  final double? confidence;
  final String? severity;
  final String analysisStatus;
  final String syncStatus;
  final String? resultJson;
  const StoredInspection({
    required this.id,
    required this.imagePath,
    required this.latitude,
    required this.longitude,
    required this.gpsAccuracy,
    this.locationName,
    required this.capturedAt,
    this.damageType,
    this.confidence,
    this.severity,
    required this.analysisStatus,
    required this.syncStatus,
    this.resultJson,
  });
  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    map['id'] = Variable<String>(id);
    map['image_path'] = Variable<String>(imagePath);
    map['latitude'] = Variable<double>(latitude);
    map['longitude'] = Variable<double>(longitude);
    map['gps_accuracy'] = Variable<double>(gpsAccuracy);
    if (!nullToAbsent || locationName != null) {
      map['location_name'] = Variable<String>(locationName);
    }
    map['captured_at'] = Variable<String>(capturedAt);
    if (!nullToAbsent || damageType != null) {
      map['damage_type'] = Variable<String>(damageType);
    }
    if (!nullToAbsent || confidence != null) {
      map['confidence'] = Variable<double>(confidence);
    }
    if (!nullToAbsent || severity != null) {
      map['severity'] = Variable<String>(severity);
    }
    map['analysis_status'] = Variable<String>(analysisStatus);
    map['sync_status'] = Variable<String>(syncStatus);
    if (!nullToAbsent || resultJson != null) {
      map['result_json'] = Variable<String>(resultJson);
    }
    return map;
  }

  InspectionRecordsCompanion toCompanion(bool nullToAbsent) {
    return InspectionRecordsCompanion(
      id: Value(id),
      imagePath: Value(imagePath),
      latitude: Value(latitude),
      longitude: Value(longitude),
      gpsAccuracy: Value(gpsAccuracy),
      locationName: locationName == null && nullToAbsent
          ? const Value.absent()
          : Value(locationName),
      capturedAt: Value(capturedAt),
      damageType: damageType == null && nullToAbsent
          ? const Value.absent()
          : Value(damageType),
      confidence: confidence == null && nullToAbsent
          ? const Value.absent()
          : Value(confidence),
      severity: severity == null && nullToAbsent
          ? const Value.absent()
          : Value(severity),
      analysisStatus: Value(analysisStatus),
      syncStatus: Value(syncStatus),
      resultJson: resultJson == null && nullToAbsent
          ? const Value.absent()
          : Value(resultJson),
    );
  }

  factory StoredInspection.fromJson(
    Map<String, dynamic> json, {
    ValueSerializer? serializer,
  }) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return StoredInspection(
      id: serializer.fromJson<String>(json['id']),
      imagePath: serializer.fromJson<String>(json['imagePath']),
      latitude: serializer.fromJson<double>(json['latitude']),
      longitude: serializer.fromJson<double>(json['longitude']),
      gpsAccuracy: serializer.fromJson<double>(json['gpsAccuracy']),
      locationName: serializer.fromJson<String?>(json['locationName']),
      capturedAt: serializer.fromJson<String>(json['capturedAt']),
      damageType: serializer.fromJson<String?>(json['damageType']),
      confidence: serializer.fromJson<double?>(json['confidence']),
      severity: serializer.fromJson<String?>(json['severity']),
      analysisStatus: serializer.fromJson<String>(json['analysisStatus']),
      syncStatus: serializer.fromJson<String>(json['syncStatus']),
      resultJson: serializer.fromJson<String?>(json['resultJson']),
    );
  }
  @override
  Map<String, dynamic> toJson({ValueSerializer? serializer}) {
    serializer ??= driftRuntimeOptions.defaultSerializer;
    return <String, dynamic>{
      'id': serializer.toJson<String>(id),
      'imagePath': serializer.toJson<String>(imagePath),
      'latitude': serializer.toJson<double>(latitude),
      'longitude': serializer.toJson<double>(longitude),
      'gpsAccuracy': serializer.toJson<double>(gpsAccuracy),
      'locationName': serializer.toJson<String?>(locationName),
      'capturedAt': serializer.toJson<String>(capturedAt),
      'damageType': serializer.toJson<String?>(damageType),
      'confidence': serializer.toJson<double?>(confidence),
      'severity': serializer.toJson<String?>(severity),
      'analysisStatus': serializer.toJson<String>(analysisStatus),
      'syncStatus': serializer.toJson<String>(syncStatus),
      'resultJson': serializer.toJson<String?>(resultJson),
    };
  }

  StoredInspection copyWith({
    String? id,
    String? imagePath,
    double? latitude,
    double? longitude,
    double? gpsAccuracy,
    Value<String?> locationName = const Value.absent(),
    String? capturedAt,
    Value<String?> damageType = const Value.absent(),
    Value<double?> confidence = const Value.absent(),
    Value<String?> severity = const Value.absent(),
    String? analysisStatus,
    String? syncStatus,
    Value<String?> resultJson = const Value.absent(),
  }) => StoredInspection(
    id: id ?? this.id,
    imagePath: imagePath ?? this.imagePath,
    latitude: latitude ?? this.latitude,
    longitude: longitude ?? this.longitude,
    gpsAccuracy: gpsAccuracy ?? this.gpsAccuracy,
    locationName: locationName.present ? locationName.value : this.locationName,
    capturedAt: capturedAt ?? this.capturedAt,
    damageType: damageType.present ? damageType.value : this.damageType,
    confidence: confidence.present ? confidence.value : this.confidence,
    severity: severity.present ? severity.value : this.severity,
    analysisStatus: analysisStatus ?? this.analysisStatus,
    syncStatus: syncStatus ?? this.syncStatus,
    resultJson: resultJson.present ? resultJson.value : this.resultJson,
  );
  StoredInspection copyWithCompanion(InspectionRecordsCompanion data) {
    return StoredInspection(
      id: data.id.present ? data.id.value : this.id,
      imagePath: data.imagePath.present ? data.imagePath.value : this.imagePath,
      latitude: data.latitude.present ? data.latitude.value : this.latitude,
      longitude: data.longitude.present ? data.longitude.value : this.longitude,
      gpsAccuracy: data.gpsAccuracy.present
          ? data.gpsAccuracy.value
          : this.gpsAccuracy,
      locationName: data.locationName.present
          ? data.locationName.value
          : this.locationName,
      capturedAt: data.capturedAt.present
          ? data.capturedAt.value
          : this.capturedAt,
      damageType: data.damageType.present
          ? data.damageType.value
          : this.damageType,
      confidence: data.confidence.present
          ? data.confidence.value
          : this.confidence,
      severity: data.severity.present ? data.severity.value : this.severity,
      analysisStatus: data.analysisStatus.present
          ? data.analysisStatus.value
          : this.analysisStatus,
      syncStatus: data.syncStatus.present
          ? data.syncStatus.value
          : this.syncStatus,
      resultJson: data.resultJson.present
          ? data.resultJson.value
          : this.resultJson,
    );
  }

  @override
  String toString() {
    return (StringBuffer('StoredInspection(')
          ..write('id: $id, ')
          ..write('imagePath: $imagePath, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('gpsAccuracy: $gpsAccuracy, ')
          ..write('locationName: $locationName, ')
          ..write('capturedAt: $capturedAt, ')
          ..write('damageType: $damageType, ')
          ..write('confidence: $confidence, ')
          ..write('severity: $severity, ')
          ..write('analysisStatus: $analysisStatus, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('resultJson: $resultJson')
          ..write(')'))
        .toString();
  }

  @override
  int get hashCode => Object.hash(
    id,
    imagePath,
    latitude,
    longitude,
    gpsAccuracy,
    locationName,
    capturedAt,
    damageType,
    confidence,
    severity,
    analysisStatus,
    syncStatus,
    resultJson,
  );
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      (other is StoredInspection &&
          other.id == this.id &&
          other.imagePath == this.imagePath &&
          other.latitude == this.latitude &&
          other.longitude == this.longitude &&
          other.gpsAccuracy == this.gpsAccuracy &&
          other.locationName == this.locationName &&
          other.capturedAt == this.capturedAt &&
          other.damageType == this.damageType &&
          other.confidence == this.confidence &&
          other.severity == this.severity &&
          other.analysisStatus == this.analysisStatus &&
          other.syncStatus == this.syncStatus &&
          other.resultJson == this.resultJson);
}

class InspectionRecordsCompanion extends UpdateCompanion<StoredInspection> {
  final Value<String> id;
  final Value<String> imagePath;
  final Value<double> latitude;
  final Value<double> longitude;
  final Value<double> gpsAccuracy;
  final Value<String?> locationName;
  final Value<String> capturedAt;
  final Value<String?> damageType;
  final Value<double?> confidence;
  final Value<String?> severity;
  final Value<String> analysisStatus;
  final Value<String> syncStatus;
  final Value<String?> resultJson;
  final Value<int> rowid;
  const InspectionRecordsCompanion({
    this.id = const Value.absent(),
    this.imagePath = const Value.absent(),
    this.latitude = const Value.absent(),
    this.longitude = const Value.absent(),
    this.gpsAccuracy = const Value.absent(),
    this.locationName = const Value.absent(),
    this.capturedAt = const Value.absent(),
    this.damageType = const Value.absent(),
    this.confidence = const Value.absent(),
    this.severity = const Value.absent(),
    this.analysisStatus = const Value.absent(),
    this.syncStatus = const Value.absent(),
    this.resultJson = const Value.absent(),
    this.rowid = const Value.absent(),
  });
  InspectionRecordsCompanion.insert({
    required String id,
    required String imagePath,
    required double latitude,
    required double longitude,
    required double gpsAccuracy,
    this.locationName = const Value.absent(),
    required String capturedAt,
    this.damageType = const Value.absent(),
    this.confidence = const Value.absent(),
    this.severity = const Value.absent(),
    required String analysisStatus,
    required String syncStatus,
    this.resultJson = const Value.absent(),
    this.rowid = const Value.absent(),
  }) : id = Value(id),
       imagePath = Value(imagePath),
       latitude = Value(latitude),
       longitude = Value(longitude),
       gpsAccuracy = Value(gpsAccuracy),
       capturedAt = Value(capturedAt),
       analysisStatus = Value(analysisStatus),
       syncStatus = Value(syncStatus);
  static Insertable<StoredInspection> custom({
    Expression<String>? id,
    Expression<String>? imagePath,
    Expression<double>? latitude,
    Expression<double>? longitude,
    Expression<double>? gpsAccuracy,
    Expression<String>? locationName,
    Expression<String>? capturedAt,
    Expression<String>? damageType,
    Expression<double>? confidence,
    Expression<String>? severity,
    Expression<String>? analysisStatus,
    Expression<String>? syncStatus,
    Expression<String>? resultJson,
    Expression<int>? rowid,
  }) {
    return RawValuesInsertable({
      if (id != null) 'id': id,
      if (imagePath != null) 'image_path': imagePath,
      if (latitude != null) 'latitude': latitude,
      if (longitude != null) 'longitude': longitude,
      if (gpsAccuracy != null) 'gps_accuracy': gpsAccuracy,
      if (locationName != null) 'location_name': locationName,
      if (capturedAt != null) 'captured_at': capturedAt,
      if (damageType != null) 'damage_type': damageType,
      if (confidence != null) 'confidence': confidence,
      if (severity != null) 'severity': severity,
      if (analysisStatus != null) 'analysis_status': analysisStatus,
      if (syncStatus != null) 'sync_status': syncStatus,
      if (resultJson != null) 'result_json': resultJson,
      if (rowid != null) 'rowid': rowid,
    });
  }

  InspectionRecordsCompanion copyWith({
    Value<String>? id,
    Value<String>? imagePath,
    Value<double>? latitude,
    Value<double>? longitude,
    Value<double>? gpsAccuracy,
    Value<String?>? locationName,
    Value<String>? capturedAt,
    Value<String?>? damageType,
    Value<double?>? confidence,
    Value<String?>? severity,
    Value<String>? analysisStatus,
    Value<String>? syncStatus,
    Value<String?>? resultJson,
    Value<int>? rowid,
  }) {
    return InspectionRecordsCompanion(
      id: id ?? this.id,
      imagePath: imagePath ?? this.imagePath,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      gpsAccuracy: gpsAccuracy ?? this.gpsAccuracy,
      locationName: locationName ?? this.locationName,
      capturedAt: capturedAt ?? this.capturedAt,
      damageType: damageType ?? this.damageType,
      confidence: confidence ?? this.confidence,
      severity: severity ?? this.severity,
      analysisStatus: analysisStatus ?? this.analysisStatus,
      syncStatus: syncStatus ?? this.syncStatus,
      resultJson: resultJson ?? this.resultJson,
      rowid: rowid ?? this.rowid,
    );
  }

  @override
  Map<String, Expression> toColumns(bool nullToAbsent) {
    final map = <String, Expression>{};
    if (id.present) {
      map['id'] = Variable<String>(id.value);
    }
    if (imagePath.present) {
      map['image_path'] = Variable<String>(imagePath.value);
    }
    if (latitude.present) {
      map['latitude'] = Variable<double>(latitude.value);
    }
    if (longitude.present) {
      map['longitude'] = Variable<double>(longitude.value);
    }
    if (gpsAccuracy.present) {
      map['gps_accuracy'] = Variable<double>(gpsAccuracy.value);
    }
    if (locationName.present) {
      map['location_name'] = Variable<String>(locationName.value);
    }
    if (capturedAt.present) {
      map['captured_at'] = Variable<String>(capturedAt.value);
    }
    if (damageType.present) {
      map['damage_type'] = Variable<String>(damageType.value);
    }
    if (confidence.present) {
      map['confidence'] = Variable<double>(confidence.value);
    }
    if (severity.present) {
      map['severity'] = Variable<String>(severity.value);
    }
    if (analysisStatus.present) {
      map['analysis_status'] = Variable<String>(analysisStatus.value);
    }
    if (syncStatus.present) {
      map['sync_status'] = Variable<String>(syncStatus.value);
    }
    if (resultJson.present) {
      map['result_json'] = Variable<String>(resultJson.value);
    }
    if (rowid.present) {
      map['rowid'] = Variable<int>(rowid.value);
    }
    return map;
  }

  @override
  String toString() {
    return (StringBuffer('InspectionRecordsCompanion(')
          ..write('id: $id, ')
          ..write('imagePath: $imagePath, ')
          ..write('latitude: $latitude, ')
          ..write('longitude: $longitude, ')
          ..write('gpsAccuracy: $gpsAccuracy, ')
          ..write('locationName: $locationName, ')
          ..write('capturedAt: $capturedAt, ')
          ..write('damageType: $damageType, ')
          ..write('confidence: $confidence, ')
          ..write('severity: $severity, ')
          ..write('analysisStatus: $analysisStatus, ')
          ..write('syncStatus: $syncStatus, ')
          ..write('resultJson: $resultJson, ')
          ..write('rowid: $rowid')
          ..write(')'))
        .toString();
  }
}

abstract class _$AppDatabase extends GeneratedDatabase {
  _$AppDatabase(QueryExecutor e) : super(e);
  $AppDatabaseManager get managers => $AppDatabaseManager(this);
  late final $InspectionRecordsTable inspectionRecords =
      $InspectionRecordsTable(this);
  @override
  Iterable<TableInfo<Table, Object?>> get allTables =>
      allSchemaEntities.whereType<TableInfo<Table, Object?>>();
  @override
  List<DatabaseSchemaEntity> get allSchemaEntities => [inspectionRecords];
}

typedef $$InspectionRecordsTableCreateCompanionBuilder =
    InspectionRecordsCompanion Function({
      required String id,
      required String imagePath,
      required double latitude,
      required double longitude,
      required double gpsAccuracy,
      Value<String?> locationName,
      required String capturedAt,
      Value<String?> damageType,
      Value<double?> confidence,
      Value<String?> severity,
      required String analysisStatus,
      required String syncStatus,
      Value<String?> resultJson,
      Value<int> rowid,
    });
typedef $$InspectionRecordsTableUpdateCompanionBuilder =
    InspectionRecordsCompanion Function({
      Value<String> id,
      Value<String> imagePath,
      Value<double> latitude,
      Value<double> longitude,
      Value<double> gpsAccuracy,
      Value<String?> locationName,
      Value<String> capturedAt,
      Value<String?> damageType,
      Value<double?> confidence,
      Value<String?> severity,
      Value<String> analysisStatus,
      Value<String> syncStatus,
      Value<String?> resultJson,
      Value<int> rowid,
    });

class $$InspectionRecordsTableFilterComposer
    extends Composer<_$AppDatabase, $InspectionRecordsTable> {
  $$InspectionRecordsTableFilterComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnFilters<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get imagePath => $composableBuilder(
    column: $table.imagePath,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get latitude => $composableBuilder(
    column: $table.latitude,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get longitude => $composableBuilder(
    column: $table.longitude,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get gpsAccuracy => $composableBuilder(
    column: $table.gpsAccuracy,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get locationName => $composableBuilder(
    column: $table.locationName,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get capturedAt => $composableBuilder(
    column: $table.capturedAt,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get damageType => $composableBuilder(
    column: $table.damageType,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<double> get confidence => $composableBuilder(
    column: $table.confidence,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get severity => $composableBuilder(
    column: $table.severity,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get analysisStatus => $composableBuilder(
    column: $table.analysisStatus,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnFilters(column),
  );

  ColumnFilters<String> get resultJson => $composableBuilder(
    column: $table.resultJson,
    builder: (column) => ColumnFilters(column),
  );
}

class $$InspectionRecordsTableOrderingComposer
    extends Composer<_$AppDatabase, $InspectionRecordsTable> {
  $$InspectionRecordsTableOrderingComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  ColumnOrderings<String> get id => $composableBuilder(
    column: $table.id,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get imagePath => $composableBuilder(
    column: $table.imagePath,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get latitude => $composableBuilder(
    column: $table.latitude,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get longitude => $composableBuilder(
    column: $table.longitude,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get gpsAccuracy => $composableBuilder(
    column: $table.gpsAccuracy,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get locationName => $composableBuilder(
    column: $table.locationName,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get capturedAt => $composableBuilder(
    column: $table.capturedAt,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get damageType => $composableBuilder(
    column: $table.damageType,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<double> get confidence => $composableBuilder(
    column: $table.confidence,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get severity => $composableBuilder(
    column: $table.severity,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get analysisStatus => $composableBuilder(
    column: $table.analysisStatus,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => ColumnOrderings(column),
  );

  ColumnOrderings<String> get resultJson => $composableBuilder(
    column: $table.resultJson,
    builder: (column) => ColumnOrderings(column),
  );
}

class $$InspectionRecordsTableAnnotationComposer
    extends Composer<_$AppDatabase, $InspectionRecordsTable> {
  $$InspectionRecordsTableAnnotationComposer({
    required super.$db,
    required super.$table,
    super.joinBuilder,
    super.$addJoinBuilderToRootComposer,
    super.$removeJoinBuilderFromRootComposer,
  });
  GeneratedColumn<String> get id =>
      $composableBuilder(column: $table.id, builder: (column) => column);

  GeneratedColumn<String> get imagePath =>
      $composableBuilder(column: $table.imagePath, builder: (column) => column);

  GeneratedColumn<double> get latitude =>
      $composableBuilder(column: $table.latitude, builder: (column) => column);

  GeneratedColumn<double> get longitude =>
      $composableBuilder(column: $table.longitude, builder: (column) => column);

  GeneratedColumn<double> get gpsAccuracy => $composableBuilder(
    column: $table.gpsAccuracy,
    builder: (column) => column,
  );

  GeneratedColumn<String> get locationName => $composableBuilder(
    column: $table.locationName,
    builder: (column) => column,
  );

  GeneratedColumn<String> get capturedAt => $composableBuilder(
    column: $table.capturedAt,
    builder: (column) => column,
  );

  GeneratedColumn<String> get damageType => $composableBuilder(
    column: $table.damageType,
    builder: (column) => column,
  );

  GeneratedColumn<double> get confidence => $composableBuilder(
    column: $table.confidence,
    builder: (column) => column,
  );

  GeneratedColumn<String> get severity =>
      $composableBuilder(column: $table.severity, builder: (column) => column);

  GeneratedColumn<String> get analysisStatus => $composableBuilder(
    column: $table.analysisStatus,
    builder: (column) => column,
  );

  GeneratedColumn<String> get syncStatus => $composableBuilder(
    column: $table.syncStatus,
    builder: (column) => column,
  );

  GeneratedColumn<String> get resultJson => $composableBuilder(
    column: $table.resultJson,
    builder: (column) => column,
  );
}

class $$InspectionRecordsTableTableManager
    extends
        RootTableManager<
          _$AppDatabase,
          $InspectionRecordsTable,
          StoredInspection,
          $$InspectionRecordsTableFilterComposer,
          $$InspectionRecordsTableOrderingComposer,
          $$InspectionRecordsTableAnnotationComposer,
          $$InspectionRecordsTableCreateCompanionBuilder,
          $$InspectionRecordsTableUpdateCompanionBuilder,
          (
            StoredInspection,
            BaseReferences<
              _$AppDatabase,
              $InspectionRecordsTable,
              StoredInspection
            >,
          ),
          StoredInspection,
          PrefetchHooks Function()
        > {
  $$InspectionRecordsTableTableManager(
    _$AppDatabase db,
    $InspectionRecordsTable table,
  ) : super(
        TableManagerState(
          db: db,
          table: table,
          createFilteringComposer: () =>
              $$InspectionRecordsTableFilterComposer($db: db, $table: table),
          createOrderingComposer: () =>
              $$InspectionRecordsTableOrderingComposer($db: db, $table: table),
          createComputedFieldComposer: () =>
              $$InspectionRecordsTableAnnotationComposer(
                $db: db,
                $table: table,
              ),
          updateCompanionCallback:
              ({
                Value<String> id = const Value.absent(),
                Value<String> imagePath = const Value.absent(),
                Value<double> latitude = const Value.absent(),
                Value<double> longitude = const Value.absent(),
                Value<double> gpsAccuracy = const Value.absent(),
                Value<String?> locationName = const Value.absent(),
                Value<String> capturedAt = const Value.absent(),
                Value<String?> damageType = const Value.absent(),
                Value<double?> confidence = const Value.absent(),
                Value<String?> severity = const Value.absent(),
                Value<String> analysisStatus = const Value.absent(),
                Value<String> syncStatus = const Value.absent(),
                Value<String?> resultJson = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => InspectionRecordsCompanion(
                id: id,
                imagePath: imagePath,
                latitude: latitude,
                longitude: longitude,
                gpsAccuracy: gpsAccuracy,
                locationName: locationName,
                capturedAt: capturedAt,
                damageType: damageType,
                confidence: confidence,
                severity: severity,
                analysisStatus: analysisStatus,
                syncStatus: syncStatus,
                resultJson: resultJson,
                rowid: rowid,
              ),
          createCompanionCallback:
              ({
                required String id,
                required String imagePath,
                required double latitude,
                required double longitude,
                required double gpsAccuracy,
                Value<String?> locationName = const Value.absent(),
                required String capturedAt,
                Value<String?> damageType = const Value.absent(),
                Value<double?> confidence = const Value.absent(),
                Value<String?> severity = const Value.absent(),
                required String analysisStatus,
                required String syncStatus,
                Value<String?> resultJson = const Value.absent(),
                Value<int> rowid = const Value.absent(),
              }) => InspectionRecordsCompanion.insert(
                id: id,
                imagePath: imagePath,
                latitude: latitude,
                longitude: longitude,
                gpsAccuracy: gpsAccuracy,
                locationName: locationName,
                capturedAt: capturedAt,
                damageType: damageType,
                confidence: confidence,
                severity: severity,
                analysisStatus: analysisStatus,
                syncStatus: syncStatus,
                resultJson: resultJson,
                rowid: rowid,
              ),
          withReferenceMapper: (p0) => p0
              .map((e) => (e.readTable(table), BaseReferences(db, table, e)))
              .toList(),
          prefetchHooksCallback: null,
        ),
      );
}

typedef $$InspectionRecordsTableProcessedTableManager =
    ProcessedTableManager<
      _$AppDatabase,
      $InspectionRecordsTable,
      StoredInspection,
      $$InspectionRecordsTableFilterComposer,
      $$InspectionRecordsTableOrderingComposer,
      $$InspectionRecordsTableAnnotationComposer,
      $$InspectionRecordsTableCreateCompanionBuilder,
      $$InspectionRecordsTableUpdateCompanionBuilder,
      (
        StoredInspection,
        BaseReferences<
          _$AppDatabase,
          $InspectionRecordsTable,
          StoredInspection
        >,
      ),
      StoredInspection,
      PrefetchHooks Function()
    >;

class $AppDatabaseManager {
  final _$AppDatabase _db;
  $AppDatabaseManager(this._db);
  $$InspectionRecordsTableTableManager get inspectionRecords =>
      $$InspectionRecordsTableTableManager(_db, _db.inspectionRecords);
}
