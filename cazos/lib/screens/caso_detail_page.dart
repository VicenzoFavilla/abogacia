import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';
import '../main.dart';
import 'anotacion_editor_page.dart';

class CasoDetailPage extends ConsumerStatefulWidget {
  final Cazo cazo;

  const CasoDetailPage({super.key, required this.cazo});

  @override
  ConsumerState<CasoDetailPage> createState() => _CasoDetailPageState();
}

class _CasoDetailPageState extends ConsumerState<CasoDetailPage> {
  // Controladores para los campos de texto, para poder leer y modificar su contenido.
  late final TextEditingController _tituloController;
  late final TextEditingController _descripcionController;

  @override
  void initState() {
    super.initState();
    // Inicializamos los controladores con los datos del "cazo" que recibimos.
    _tituloController = TextEditingController(text: widget.cazo.titulo);
    _descripcionController = TextEditingController(text: widget.cazo.descripcion);
  }

  @override
  void dispose() {
    // Es importante limpiar los controladores cuando la pantalla se destruye.
    _tituloController.dispose();
    _descripcionController.dispose();
    super.dispose();
  }

  Future<void> _guardarCambios() async {
    final apiService = ref.read(apiServiceProvider);
    final scaffoldMessenger = ScaffoldMessenger.of(context);

    try {
      // Creamos el mapa de datos con la información actualizada de los controladores.
      final datosActualizados = {
        'titulo': _tituloController.text,
        'descripcion': _descripcionController.text,
        // Aquí podrías añadir otros campos como 'tipo' o 'estado' si los tuvieras.
      };

      // Llamamos al nuevo método de la API para actualizar.
      await apiService.updateCazo(widget.cazo.id, datosActualizados);

      // Invalidamos el provider para que la lista principal se refresque al volver.
      ref.invalidate(cazosProvider);

      scaffoldMessenger.showSnackBar(
        const SnackBar(content: Text('Cazo guardado con éxito'), backgroundColor: Colors.green),
      );

      // Volvemos a la pantalla anterior.
      Navigator.of(context).pop();

    } catch (e) {
      scaffoldMessenger.showSnackBar(
        SnackBar(content: Text('Error al guardar: $e'), backgroundColor: Colors.red),
      );
    }
  }

  Future<void> _descargarYAbrirDocumento(int documentoId) async {
    final baseUrl = ref.read(apiServiceProvider).getBaseUrl();
    final url = Uri.parse('$baseUrl/documentos/$documentoId/descargar');

    // Usamos `mounted` para asegurarnos de que el widget todavía está en el árbol
    // antes de mostrar un SnackBar.
    if (!mounted) return;

    if (await canLaunchUrl(url)) {
      // Le pedimos al sistema operativo que abra el archivo en la app externa correspondiente.
      await launchUrl(url, mode: LaunchMode.externalApplication);
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('No se pudo abrir el documento: $url'), backgroundColor: Colors.red),
      );
    }
  }

  String _parseQuillJson(String jsonString) {
    try {
      final List<dynamic> delta = jsonDecode(jsonString);
      final plainText = delta.map((e) => e['insert']).join();
      // Limita el texto para la vista previa y elimina saltos de línea.
      return plainText.replaceAll('\n', ' ').substring(0, (plainText.length > 100) ? 100 : plainText.length);
    } catch (e) {
      return "Contenido inválido";
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.cazo.titulo),
        actions: [
          // Botón para guardar los cambios
          IconButton(
            icon: const Icon(Icons.save),
            onPressed: _guardarCambios,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.of(context).push(MaterialPageRoute(
            builder: (context) => AnotacionEditorPage(casoId: widget.cazo.id),
          ));
        },
        child: const Icon(Icons.add_comment),
        tooltip: 'Nueva Anotación',
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView( // Hacemos que la pantalla sea scrollable
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TextField(
                controller: _tituloController,
                decoration: const InputDecoration(
                  labelText: 'Título',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _descripcionController,
                decoration: const InputDecoration(
                  labelText: 'Descripción',
                  border: OutlineInputBorder(),
                ),
                maxLines: 5,
              ),
              const SizedBox(height: 24),
              Text('Documentos Asociados', style: Theme.of(context).textTheme.titleLarge),
              const Divider(),
              // Usamos un Consumer para reconstruir solo la lista de documentos
              Consumer(
                builder: (context, ref, child) {
                  final asyncDocumentos = ref.watch(documentosProvider(widget.cazo.id));
                  return asyncDocumentos.when(
                    loading: () => const Center(child: CircularProgressIndicator()),
                    error: (err, stack) => Center(child: Text('Error: $err')),
                    data: (documentos) {
                      if (documentos.isEmpty) {
                        return const Center(child: Padding(
                          padding: EdgeInsets.all(16.0),
                          child: Text('No hay documentos para este caso.'),
                        ));
                      }
                      // Usamos ListView.separated para tener divisores entre elementos
                      return ListView.separated(
                        shrinkWrap: true, // Para que funcione dentro de un SingleChildScrollView
                        physics: const NeverScrollableScrollPhysics(), // El scroll lo maneja el padre
                        itemCount: documentos.length,
                        separatorBuilder: (context, index) => const Divider(),
                        itemBuilder: (context, index) {
                          final documento = documentos[index];
                          return ListTile(
                            leading: const Icon(Icons.description_outlined),
                            title: Text(documento.nombre),
                            subtitle: Text(documento.tipo ?? 'Sin tipo'),
                            onTap: () => _descargarYAbrirDocumento(documento.id),
                          );
                        },
                      );
                    },
                  );
                },
              ),
              const SizedBox(height: 24),
              Text('Anotaciones', style: Theme.of(context).textTheme.titleLarge),
              const Divider(),
              Consumer(
                builder: (context, ref, child) {
                  final asyncAnotaciones = ref.watch(anotacionesProvider(widget.cazo.id));
                  return asyncAnotaciones.when(
                    loading: () => const Center(child: CircularProgressIndicator()),
                    error: (err, stack) => Center(child: Text('Error: $err')),
                    data: (anotaciones) {
                      if (anotaciones.isEmpty) {
                        return const Center(child: Padding(
                          padding: EdgeInsets.all(16.0),
                          child: Text('No hay anotaciones. ¡Añade una!'),
                        ));
                      }
                      return ListView.builder(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: anotaciones.length,
                        itemBuilder: (context, index) {
                          final anotacion = anotaciones[index];
                          return ListTile(
                            leading: const Icon(Icons.note_alt_outlined),
                            title: Text(anotacion.autor ?? 'Anónimo'),
                            subtitle: Text(_parseQuillJson(anotacion.texto), maxLines: 2, overflow: TextOverflow.ellipsis),
                            onTap: () => Navigator.of(context).push(MaterialPageRoute(builder: (context) => AnotacionEditorPage(casoId: widget.cazo.id, anotacion: anotacion))),
                          );
                        },
                      );
                    },
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}