import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  String error = '';
  bool loading = false;

  void _login() async {
    setState(() {
      loading = true;
      error = '';
    });

    final result = await ApiService.login(
      _usernameController.text,
      _passwordController.text,
    );

    if (result['ok']) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => const HomeScreen()),
      );
    } else {
      setState(() {
        error = result['message'] ?? 'Error desconocido';
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text("Iniciar sesión en GestorDocs", style: TextStyle(fontSize: 24)),
                const SizedBox(height: 24),
                TextFormField(
                  controller: _usernameController,
                  decoration: const InputDecoration(labelText: 'Usuario'),
                  validator: (value) => value!.isEmpty ? 'Ingrese su usuario' : null,
                ),
                TextFormField(
                  controller: _passwordController,
                  decoration: const InputDecoration(labelText: 'Contraseña'),
                  obscureText: true,
                  validator: (value) => value!.isEmpty ? 'Ingrese su contraseña' : null,
                ),
                const SizedBox(height: 16),
                if (error.isNotEmpty) Text(error, style: const TextStyle(color: Colors.red)),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: loading ? null : () {
                    if (_formKey.currentState!.validate()) _login();
                  },
                  child: loading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text("Iniciar sesión"),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
