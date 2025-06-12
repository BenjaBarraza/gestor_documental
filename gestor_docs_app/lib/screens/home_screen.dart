import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'login_screen.dart';
import 'document_list_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  void _logout(BuildContext context) async {
    await ApiService.logout();
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
    );
  }

  void _goToDocumentos(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const DocumentListScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Inicio - GestorDocs"),
        actions: [
          IconButton(
            onPressed: () => _logout(context),
            icon: const Icon(Icons.logout),
            tooltip: 'Cerrar sesión',
          )
        ],
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                "Bienvenido, usuario autenticado.",
                style: textTheme.bodyMedium?.copyWith(fontSize: 18),
              ),
              const SizedBox(height: 24),
              ElevatedButton.icon(
                onPressed: () => _goToDocumentos(context),
                icon: const Icon(Icons.folder),
                label: const Text("Ver documentos"),
                style: ElevatedButton.styleFrom(
                  foregroundColor: colorScheme.onPrimary,
                  backgroundColor: colorScheme.primaryContainer,
                  textStyle: const TextStyle(fontSize: 16),
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
