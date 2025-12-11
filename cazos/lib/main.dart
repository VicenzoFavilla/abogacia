import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:dio/dio.dart';
import 'screens/caso_detail_page.dart';
import 'dart:convert';

void main() {
  // Para usar Riverpod, envolvemos la aplicación en un ProviderScope.
  runApp(const ProviderScope(child: MyApp()));
}

// --- MODELO DE DATOS ---
class Cazo {
  final int id;
  final String titulo;
  final String descripcion;

  Cazo({
    required this.id,
    required this.titulo,
    required this.descripcion,
  });

  factory Cazo.fromJson(Map<String, dynamic> json) {
    return Cazo(
      id: json['id'],
      titulo: json['titulo'] ?? 'Sin título',
      descripcion: json['descripcion'] ?? 'Sin descripción',
    );
  }
}

// --- MODELO DE DATOS PARA DOCUMENTO ---
class Documento {
  final int id;
  final String nombre;
  final String? tipo;

  Documento({
    required this.id,
    required this.nombre,
    this.tipo,
  });

  factory Documento.fromJson(Map<String, dynamic> json) {
    return Documento(
      id: json['id'],
      nombre: json['nombre'] ?? 'Sin nombre',
      tipo: json['tipo'],
    );
  }
}

// --- MODELO DE DATOS PARA ANOTACION ---
class Anotacion {
  final int id;
  final String texto; // Guardaremos el JSON del editor de texto aquí
  final String? autor;
  final DateTime fecha;
  final int casoId;

  Anotacion({
    required this.id,
    required this.texto,
    this.autor,
    required this.fecha,
    required this.casoId,
  });

  factory Anotacion.fromJson(Map<String, dynamic> json) {
    return Anotacion(
      id: json['id'],
      texto: json['texto'] ?? '',
      autor: json['autor'],
      fecha: DateTime.parse(json['fecha']),
      casoId: json['caso_id'],
    );
  }
}

// --- SERVICIO DE API ---
class ApiService {
  // Leemos la URL base de la API desde las variables de entorno pasadas en la compilación.
  // Esto nos permite cambiar la IP sin modificar el código.
  static const String _baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000', // Un valor por defecto para evitar errores.
  );
  final Dio _dio = Dio(BaseOptions(baseUrl: _baseUrl));

  // Getter para que otras partes de la app puedan conocer la URL base.
  String getBaseUrl() => _baseUrl;

  Future<List<Cazo>> getCazos() async {
    try {
      // Apuntamos al endpoint correcto de tu backend: /casos
      final response = await _dio.get('/casos');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => Cazo.fromJson(json)).toList();
      } else {
        throw Exception('Error del servidor: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Fallo al cargar los cazos: $e');
    }
  }

  Future<void> updateCazo(int id, Map<String, dynamic> data) async {
    try {
      final response = await _dio.put('/casos/$id', data: data);
      if (response.statusCode != 200) {
        throw Exception('Error del servidor al actualizar: ${response.statusCode}');
      }
    } catch (e) {
      // Re-lanzamos la excepción para que la UI pueda manejarla.
      throw Exception('Fallo al actualizar el cazo: $e');
    }
  }

  Future<List<Documento>> getDocumentosPorCaso(int casoId) async {
    try {
      final response = await _dio.get('/casos/$casoId/documentos');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => Documento.fromJson(json)).toList();
      } else {
        throw Exception('Error del servidor al cargar documentos: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Fallo al cargar los documentos: $e');
    }
  }

  Future<List<Anotacion>> getAnotacionesPorCaso(int casoId) async {
    try {
      final response = await _dio.get('/anotaciones/caso/$casoId');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => Anotacion.fromJson(json)).toList();
      } else {
        throw Exception('Error del servidor al cargar anotaciones: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Fallo al cargar las anotaciones: $e');
    }
  }

  Future<Anotacion> createAnotacion(int casoId, Map<String, dynamic> data) async {
    final response = await _dio.post('/anotaciones/?caso_id=$casoId', data: data);
    if (response.statusCode == 200) {
      return Anotacion.fromJson(response.data);
    } else {
      throw Exception('Fallo al crear la anotación');
    }
  }

  Future<Anotacion> updateAnotacion(int anotacionId, Map<String, dynamic> data) async {
    final response = await _dio.put('/anotaciones/$anotacionId', data: data);
    if (response.statusCode == 200) {
      return Anotacion.fromJson(response.data);
    } else {
      throw Exception('Fallo al actualizar la anotación');
    }
  }
}

// --- PROVEEDORES DE RIVERPOD ---

// 1. Provider para nuestro servicio de API.
final apiServiceProvider = Provider<ApiService>((ref) => ApiService());

// 2. FutureProvider que usa el servicio para obtener los datos.
//    Riverpod manejará automáticamente los estados de carga y error.
final cazosProvider = FutureProvider<List<Cazo>>((ref) {
  // "watch" obtiene el servicio y se asegura de que este provider se reconstruya si el servicio cambia.
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getCazos();
});

// 3. Provider para los documentos de un caso específico.
//    Usamos .family para poder pasarle el ID del caso.
final documentosProvider = FutureProvider.family<List<Documento>, int>((ref, casoId) {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getDocumentosPorCaso(casoId);
});

// 4. Provider para las anotaciones de un caso específico.
final anotacionesProvider = FutureProvider.family<List<Anotacion>, int>((ref, casoId) {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getAnotacionesPorCaso(casoId);
});

// --- UI (WIDGETS) ---

class MyApp extends ConsumerWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return MaterialApp(
      title: 'Gestor de Cazos',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const CazosListPage(),
    );
  }
}

class CazosListPage extends ConsumerWidget {
  const CazosListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // "watch" escucha los cambios en el provider.
    final asyncCazos = ref.watch(cazosProvider);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('Lista de Cazos'),
      ),
      // El método .when de Riverpod es perfecto para manejar los 3 estados de un Future.
      body: asyncCazos.when(
        // 1. Estado de carga
        loading: () => const Center(child: CircularProgressIndicator()),
        // 2. Estado de error
        error: (err, stack) => Center(child: Text('Error: $err')),
        // 3. Estado de éxito (datos recibidos)
        data: (cazos) {
          return ListView.builder(
            itemCount: cazos.length,
            itemBuilder: (context, index) {
              final cazo = cazos[index];
              return ListTile(
                leading: CircleAvatar(child: Text(cazo.id.toString())),
                title: Text(cazo.titulo),
                subtitle: Text(cazo.descripcion, maxLines: 1, overflow: TextOverflow.ellipsis),
                onTap: () {
                  // Navegamos a la pantalla de detalle al tocar un elemento.
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => CasoDetailPage(cazo: cazo)),
                  );
                },
              );
            },
          );
        },
      ),
    );
  }
}
