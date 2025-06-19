import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';
import '../services/api_service.dart';

class SubirDocumentoScreen extends StatefulWidget {
  const SubirDocumentoScreen({super.key});

  @override
  State<SubirDocumentoScreen> createState() => _SubirDocumentoScreenState();
}

class _SubirDocumentoScreenState extends State<SubirDocumentoScreen> {
  PlatformFile? archivoSeleccionado;
  bool subiendo = false;
  String? mensaje;

  Future<void> seleccionarArchivo() async {
    final resultado = await FilePicker.platform.pickFiles();

    if (resultado != null && resultado.files.isNotEmpty) {
      setState(() {
        archivoSeleccionado = resultado.files.first;
        mensaje = null;
      });
    }
  }

  Future<void> subirArchivo() async {
    if (archivoSeleccionado == null) return;

    setState(() {
      subiendo = true;
      mensaje = null;
    });

    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access');

    final uri = Uri.parse('${ApiService.baseUrl}/documentos/');
    final request = http.MultipartRequest('POST', uri)
      ..headers['Authorization'] = 'Bearer $token'
      ..fields['nombre'] = archivoSeleccionado!.name;

    if (archivoSeleccionado!.bytes != null) {
      request.files.add(http.MultipartFile.fromBytes(
        'archivo',
        archivoSeleccionado!.bytes!,
        filename: archivoSeleccionado!.name,
      ));
    } else {
      request.files.add(await http.MultipartFile.fromPath(
        'archivo',
        archivoSeleccionado!.path!,
        filename: archivoSeleccionado!.name,
      ));
    }

    final response = await request.send();

    setState(() {
      subiendo = false;
      if (response.statusCode == 201) {
        mensaje = '✅ Documento subido correctamente';
        archivoSeleccionado = null;
      } else {
        mensaje = '❌ Error al subir el documento';
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Subir documento"),
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
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                archivoSeleccionado != null
                    ? Column(
                        children: [
                          const Icon(Icons.insert_drive_file, size: 64, color: Colors.deepPurpleAccent),
                          const SizedBox(height: 8),
                          Text(
                            archivoSeleccionado!.name,
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: Colors.white),
                          ),
                          const SizedBox(height: 16),
                        ],
                      )
                    : const Text(
                        "No se ha seleccionado ningún archivo",
                        style: TextStyle(color: Colors.white70),
                      ),
                const SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: subiendo ? null : seleccionarArchivo,
                  icon: const Icon(Icons.upload_file),
                  label: const Text("Seleccionar archivo"),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: (archivoSeleccionado != null && !subiendo) ? subirArchivo : null,
                  icon: const Icon(Icons.cloud_upload),
                  label: subiendo
                      ? const Text("Subiendo...")
                      : const Text("Subir documento"),
                ),
                const SizedBox(height: 24),
                if (mensaje != null)
                  Text(
                    mensaje!,
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: mensaje!.startsWith('✅') ? Colors.greenAccent : Colors.redAccent,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
