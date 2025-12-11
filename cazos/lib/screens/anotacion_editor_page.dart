import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_quill/flutter_quill.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../main.dart';

class AnotacionEditorPage extends ConsumerStatefulWidget {
  final int casoId;
  final Anotacion? anotacion; // Si es null, es una nueva anotación.

  const AnotacionEditorPage({
    super.key,
    required this.casoId,
    this.anotacion,
  });

  @override
  ConsumerState<AnotacionEditorPage> createState() => _AnotacionEditorPageState();
}

class _AnotacionEditorPageState extends ConsumerState<AnotacionEditorPage> {
  late QuillController _controller;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _initController();
  }

  void _initController() {
    // Si estamos editando una anotación existente, cargamos su contenido.
    if (widget.anotacion != null && widget.anotacion!.texto.isNotEmpty) {
      try {
        final doc = Document.fromJson(jsonDecode(widget.anotacion!.texto));
        _controller = QuillController(
          document: doc,
          selection: const TextSelection.collapsed(offset: 0),
        );
      } catch (e) {
        // Si el JSON es inválido, empezamos con un documento en blanco.
        _controller = QuillController.basic();
      }
    } else {
      // Si es una nueva anotación, empezamos con un documento en blanco.
      _controller = QuillController.basic();
    }
  }

  Future<void> _guardarAnotacion() async {
    setState(() => _isLoading = true);
    final apiService = ref.read(apiServiceProvider);
    final scaffoldMessenger = ScaffoldMessenger.of(context);

    // Convertimos el contenido del editor a una cadena JSON.
    final contenidoJson = jsonEncode(_controller.document.toDelta().toJson());

    try {
      if (widget.anotacion == null) {
        // Crear nueva anotación
        await apiService.createAnotacion(widget.casoId, {'texto': contenidoJson, 'autor': 'Usuario'});
      } else {
        // Actualizar anotación existente
        await apiService.updateAnotacion(widget.anotacion!.id, {'texto': contenidoJson, 'autor': 'Usuario'});
      }

      // Refrescamos la lista de anotaciones en la pantalla de detalle.
      ref.invalidate(anotacionesProvider(widget.casoId));
      scaffoldMessenger.showSnackBar(const SnackBar(content: Text('Guardado'), backgroundColor: Colors.green));
      Navigator.of(context).pop();

    } catch (e) {
      scaffoldMessenger.showSnackBar(SnackBar(content: Text('Error al guardar: $e'), backgroundColor: Colors.red));
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.anotacion == null ? 'Nueva Anotación' : 'Editar Anotación'),
        actions: [
          if (_isLoading) const CircularProgressIndicator() else IconButton(icon: const Icon(Icons.save), onPressed: _guardarAnotacion),
        ],
      ),
      body: Column(
        children: [
          QuillToolbar.simple(
            configurations: QuillSimpleToolbarConfigurations(
              controller: _controller,
            ),
          ),
          const Divider(),
          Expanded(
            child: QuillEditor.basic(
              configurations: QuillEditorBasicConfigurations(
                controller: _controller,
                readOnly: false,
              ),
            ),
          ),
        ],
      ),
    );
  }
}