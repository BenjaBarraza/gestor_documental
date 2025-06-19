import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/api_service.dart';
import 'login_screen.dart';
import 'document_list_screen.dart';
import 'profile_screen.dart';
import 'subir_documento_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String? username;
  bool loadingUser = true;
  bool animateIcon = false;

  @override
  void initState() {
    super.initState();
    _fetchUsername();
    Future.delayed(const Duration(milliseconds: 300), () {
      if (mounted) setState(() => animateIcon = true);
    });
  }

  Future<void> _fetchUsername() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access');

    if (token == null) {
      setState(() {
        loadingUser = false;
      });
      return;
    }

    final url = Uri.parse('${ApiService.baseUrl}/perfil/');
    try {
      final res = await http.get(
        url,
        headers: {'Authorization': 'Bearer $token'},
      );

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          username = data['username'];
          loadingUser = false;
        });
      } else {
        setState(() => loadingUser = false);
      }
    } catch (_) {
      setState(() => loadingUser = false);
    }
  }

  void _logout() async {
    await ApiService.logout();
    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  void _goToDocumentos() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const DocumentListScreen()),
    );
  }

  void _goToPerfil() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const ProfileScreen()),
    );
  }

  void _goToSubirDocumento() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const SubirDocumentoScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Inicio - GestorDocs"),
      ),
      drawer: Drawer(
        child: ListView(
          padding: const EdgeInsets.symmetric(vertical: 0),
          children: [
            DrawerHeader(
              decoration: const BoxDecoration(color: Colors.deepPurple),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const CircleAvatar(
                    radius: 30,
                    backgroundColor: Colors.white,
                    child: Icon(Icons.person, size: 30, color: Colors.deepPurple),
                  ),
                  const SizedBox(height: 12),
                  loadingUser
                      ? const CircularProgressIndicator(color: Colors.white)
                      : Text(
                          username != null
                              ? 'Hola, $username'
                              : 'Usuario desconocido',
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                          ),
                        ),
                ],
              ),
            ),
            ListTile(
              leading: const Icon(Icons.folder),
              title: const Text("Ver documentos"),
              onTap: () {
                Navigator.pop(context);
                _goToDocumentos();
              },
            ),
            ListTile(
              leading: const Icon(Icons.person),
              title: const Text("Ver perfil"),
              onTap: () {
                Navigator.pop(context);
                _goToPerfil();
              },
            ),
            ListTile(
              leading: const Icon(Icons.upload_file),
              title: const Text("Subir documento"),
              onTap: () {
                Navigator.pop(context);
                _goToSubirDocumento();
              },
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.logout),
              title: const Text("Cerrar sesión"),
              onTap: _logout,
            ),
          ],
        ),
      ),
      body: Container(
        width: double.infinity,
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF0E0E10), Color(0xFF1F1F25)],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedSlide(
              offset: animateIcon ? Offset.zero : const Offset(0, 0.3),
              duration: const Duration(milliseconds: 600),
              curve: Curves.easeOut,
              child: AnimatedOpacity(
                opacity: animateIcon ? 1 : 0,
                duration: const Duration(milliseconds: 800),
                child: AnimatedScale(
                  scale: animateIcon ? 1 : 0.85,
                  duration: const Duration(milliseconds: 600),
                  child: const Icon(
                    Icons.description_rounded,
                    size: 80,
                    color: Colors.deepPurpleAccent,
                  ),
                ),
              ),
            ),
            const SizedBox(height: 24),
            Card(
              elevation: 4,
              margin: const EdgeInsets.symmetric(horizontal: 32),
              color: Colors.deepPurple.withOpacity(0.1),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: loadingUser
                    ? const CircularProgressIndicator(color: Colors.white)
                    : Text(
                        username != null
                            ? "👋 ¡Bienvenido $username!\nGestiona tus archivos y comparte con seguridad."
                            : "👋 ¡Hola!\nGestiona tus archivos y comparte con seguridad.",
                        textAlign: TextAlign.center,
                        style: textTheme.bodyMedium?.copyWith(
                          color: Colors.white,
                          fontSize: 16,
                        ),
                      ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
