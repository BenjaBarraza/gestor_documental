import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/api_service.dart';
import 'login_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String? username;
  String? email;
  String? tipoCuenta;
  String? error;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    fetchPerfil();
  }

  Future<void> fetchPerfil() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access');

    if (token == null) {
      setState(() {
        error = 'No has iniciado sesión.';
        loading = false;
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
          email = data['email'];
          tipoCuenta = data['tipo_cuenta'];
          loading = false;
        });
      } else if (res.statusCode == 401) {
        await prefs.clear();
        if (!mounted) return;
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const LoginScreen()),
        );
      } else {
        setState(() {
          error = 'Error ${res.statusCode}: ${res.reasonPhrase}';
          loading = false;
        });
      }
    } catch (e) {
      setState(() {
        error = 'Error de red: $e';
        loading = false;
      });
    }
  }

  void logout() async {
    await ApiService.logout();
    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mi perfil')),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : error != null
              ? Center(child: Text(error!, style: const TextStyle(color: Colors.red)))
              : Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Usuario: $username', style: const TextStyle(fontSize: 18)),
                      const SizedBox(height: 12),
                      Text('Correo: $email', style: const TextStyle(fontSize: 18)),
                      const SizedBox(height: 12),
                      Text('Tipo de cuenta: $tipoCuenta', style: const TextStyle(fontSize: 18)),
                      const Spacer(),
                      Center(
                        child: ElevatedButton.icon(
                          onPressed: logout,
                          icon: const Icon(Icons.logout),
                          label: const Text('Cerrar sesión'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.deepPurple,
                            padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                          ),
                        ),
                      )
                    ],
                  ),
                ),
    );
  }
}
