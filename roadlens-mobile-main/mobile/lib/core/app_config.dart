class AppConfig {
  const AppConfig({required this.environment, required this.apiBaseUrl});

  factory AppConfig.fromEnvironment() {
    const environment = String.fromEnvironment(
      'APP_ENV',
      defaultValue: 'development',
    );
    const apiBaseUrl = String.fromEnvironment(
      'API_BASE_URL',
      defaultValue: 'http://10.0.2.2:4173',
    );
    final uri = Uri.tryParse(apiBaseUrl);
    if (uri == null || !uri.hasScheme || !uri.hasAuthority) {
      throw StateError('API_BASE_URL must be an absolute URL.');
    }
    if (environment == 'production' && uri.scheme != 'https') {
      throw StateError('Production API_BASE_URL must use HTTPS.');
    }
    return const AppConfig(environment: environment, apiBaseUrl: apiBaseUrl);
  }

  final String environment;
  final String apiBaseUrl;
}
