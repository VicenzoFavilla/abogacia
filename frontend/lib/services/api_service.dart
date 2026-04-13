import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/foundation.dart';

class ApiService {
  final Dio _dio = Dio(BaseOptions(
    // Backend URL. Reemplazar si se ejecuta desde dispositivo físico
    baseUrl: 'http://127.0.0.1:8010',
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 10),
  ));

  ApiService() {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final prefs = await SharedPreferences.getInstance();
        final token = prefs.getString('access_token');
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
    ));
  }

  // --- Autenticación ---

  Future<bool> login(String email, String password) async {
    try {
      final response = await _dio.post(
        '/auth/login', 
        data: {
          'username': email,
          'password': password,
        },
        options: Options(contentType: Headers.formUrlEncodedContentType)
      );
      
      if (response.statusCode == 200) {
        final token = response.data['access_token'];
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('access_token', token);
        return true;
      }
      return false;
    } on DioException catch (e) {
      if (e.response != null && e.response?.statusCode == 401) {
        throw Exception("Email o contraseña incorrecta");
      }
      throw Exception("CORS/Red: ${e.message}");
    } catch (e) {
      throw Exception(e.toString());
    }
  }

  Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
  }

  // --- Documentos y Editor ---

  Future<List<dynamic>> getDocumentos() async {
    try {
      final response = await _dio.get('/documentos/');
      return response.data;
    } catch (e) {
      throw Exception('Error al cargar documentos: $e');
    }
  }

  /// Trae el contenido editable (HTML) de un documento Word o TXT
  Future<Map<String, dynamic>> getContenidoEditable(int id) async {
    try {
      final response = await _dio.get('/documentos/$id/contenido');
      return response.data;
    } catch (e) {
      throw Exception('Error al cargar contenido editable: $e');
    }
  }

  Future<void> subirDocumento(String fname, List<int> bytes, int casoId) async {
    try {
      final formData = FormData.fromMap({
        'archivo': MultipartFile.fromBytes(bytes, filename: fname),
        'nombre': fname,
        'caso_id': casoId,
      });

      await _dio.post('/documentos/', data: formData);
    } catch (e) {
      throw Exception('Error al subir documento: $e');
    }
  }

  Future<void> actualizarDocumento(int id, String? nombre, String? tipo) async {
    try {
      final formData = FormData.fromMap({
        if (nombre != null) 'nombre': nombre,
        if (tipo != null) 'tipo': tipo,
      });
      await _dio.put('/documentos/$id', data: formData);
    } catch (e) {
      throw Exception('Error al actualizar documento: $e');
    }
  }

  /// Guarda el contenido HTML del documento (Auto-guardado)
  Future<void> guardarContenidoEditable(int id, String htmlVal) async {
    try {
      await _dio.put('/documentos/$id/contenido', data: {
        'contenido_html': htmlVal,
        'es_autoguardado': true,
      });
    } catch (e) {
      throw Exception('Error al auto-guardar: $e');
    }
  }

  // --- Colecciones ---
  Future<List<dynamic>> getColecciones() async {
    try {
      final response = await _dio.get('/colecciones/');
      return response.data;
    } catch (e) {
      throw Exception('Error al cargar colecciones: $e');
    }
  }

  Future<void> crearColeccion(String nombre) async {
    try {
      await _dio.post('/colecciones/', data: {
        'nombre': nombre,
      });
    } catch (e) {
      throw Exception('Error al crear colección: $e');
    }
  }
}

// Global provider instance
final apiService = ApiService();
