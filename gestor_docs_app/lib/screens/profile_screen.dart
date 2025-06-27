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
  String username = '';
  String email = '';
  String tipoCuenta = '';
  int totalDocumentos = 0;
  bool loading = true;

  @override
  void initState() {
    super.initState();
    fetchPerfil();
  }

  Future<void> fetchPerfil() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access');

    if (token == null) return;

    final perfilUrl = Uri.parse('${ApiService.baseUrl}/perfil/');
    final docsUrl = Uri.parse('${ApiService.baseUrl}/documentos/');

    try {
      final perfilRes = await http.get(
        perfilUrl,
        headers: {'Authorization': 'Bearer $token'},
      );

      final docsRes = await http.get(
        docsUrl,
        headers: {'Authorization': 'Bearer $token'},
      );

      if (perfilRes.statusCode == 200) {
        final perfilData = jsonDecode(perfilRes.body);
        setState(() {
          username = perfilData['username'];
          email = perfilData['email'];
          tipoCuenta = perfilData['tipo_cuenta'];
        });
      }

      if (docsRes.statusCode == 200) {
        final List documentos = jsonDecode(docsRes.body);
        setState(() {
          totalDocumentos = documentos.length;
        });
      }
    } catch (e) {
      debugPrint('Error al cargar perfil: $e');
    } finally {
      setState(() => loading = false);
    }
  }

  void _performLogout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        title: const Text('¿Cerrar sesión?'),
        content: const Text('¿Estás seguro de que deseas cerrar sesión?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _performLogout();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red[600],
              foregroundColor: Colors.white,
            ),
            child: const Text('Cerrar sesión'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return loading
        ? const Scaffold(body: Center(child: CircularProgressIndicator()))
        : Scaffold(
            backgroundColor: Colors.grey[50],
            body: CustomScrollView(
              slivers: [
                SliverAppBar(
                  expandedHeight: 200,
                  pinned: true,
                  backgroundColor: const Color(0xFF1565C0),
                  flexibleSpace: FlexibleSpaceBar(
                    title: const Text('Mi Perfil', style: TextStyle(color: Colors.white)),
                    background: Container(
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [Color(0xFF1976D2), Color(0xFF1565C0)],
                        ),
                      ),
                      child: const Center(
                        child: CircleAvatar(
                          radius: 50,
                          backgroundColor: Colors.white,
                          child: Icon(Icons.person, size: 60, color: Color(0xFF1565C0)),
                        ),
                      ),
                    ),
                  ),
                ),
                SliverToBoxAdapter(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      children: [
                        _buildInfoCard(),
                        const SizedBox(height: 16),
                        _buildStatsCard(),
                        const SizedBox(height: 24),
                        _buildLogoutButton(),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          );
  }

  Widget _buildInfoCard() {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            _buildInfoRow(Icons.person_outline, 'Usuario', username),
            const Divider(height: 24),
            _buildInfoRow(Icons.email_outlined, 'Correo electrónico', email),
            const Divider(height: 24),
            _buildInfoRow(Icons.account_circle_outlined, 'Tipo de cuenta', tipoCuenta),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Row(
      children: [
        Icon(icon, color: Colors.grey[600]),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(label, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              const SizedBox(height: 4),
              Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildStatsCard() {
    return Card(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Row(
              children: [
                Icon(Icons.analytics_outlined, color: Colors.blue[700]),
                const SizedBox(width: 8),
                const Text(
                  'Estadísticas',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: _buildStatItem(Icons.description, 'Documentos', '$totalDocumentos', Colors.blue)),
                Expanded(child: _buildStatItem(Icons.folder, 'Carpetas', '0', Colors.orange)),
                Expanded(child: _buildStatItem(Icons.cloud_upload, 'Subidos hoy', '0', Colors.green)),
              ],
            )
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(IconData icon, String label, String value, Color color) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 4),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(8)),
      child: Column(
        children: [
          Icon(icon, color: color),
          const SizedBox(height: 8),
          Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 18)),
          const SizedBox(height: 4),
          Text(label, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
        ],
      ),
    );
  }

  Widget _buildLogoutButton() {
    return SizedBox(
      width: double.infinity,
      height: 50,
      child: ElevatedButton.icon(
        onPressed: _showLogoutDialog,
        icon: const Icon(Icons.logout),
        label: const Text('Cerrar Sesión'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.red[600],
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
    );
  }
}
