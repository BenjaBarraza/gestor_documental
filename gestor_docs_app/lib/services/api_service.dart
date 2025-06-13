import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

enum Modo { localWifi, localEmulador, produccion }

class ApiService {
  // Cambia solo esta línea:
  static const Modo modo = Modo.localWifi;

  static final String baseUrl = switch (modo) {
    Modo.localWifi => 'http://192.168.18.173:8000/api',
    Modo.localEmulador => 'http://localhost:8000/api',
    Modo.produccion => 'https://gestor-documental-c1tp.onrender.com/api',
  };

  static Future<Map<String, dynamic>> login(String username, String password) async {
    final url = Uri.parse('$baseUrl/token/');
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'username': username, 'password': password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('access', data['access']);
        await prefs.setString('refresh', data['refresh']);
        return {'ok': true};
      } else {
        final data = jsonDecode(response.body);
        return {'ok': false, 'message': data['detail'] ?? 'Credenciales inválidas'};
      }
    } catch (e) {
      return {'ok': false, 'message': 'Error de red: $e'};
    }
  }

  static Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.containsKey('access');
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }
}
