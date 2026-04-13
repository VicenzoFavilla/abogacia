import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_quill/flutter_quill.dart';
import 'package:flutter_quill/quill_delta.dart'; // import necesario si hay conversiones
import 'package:abogacia_frontend/services/api_service.dart';

// Nota: en un entorno de producción, puedes usar `delta_markdown` u otra lib 
// para convertir entre HTML y Delta de Quill. Para este MVP simulamos un HTML simple.

class DocumentEditor extends StatefulWidget {
  final int documentoId;
  final String nombre;

  const DocumentEditor({Key? key, required this.documentoId, required this.nombre}) : super(key: key);

  @override
  State<DocumentEditor> createState() => _DocumentEditorState();
}

class _DocumentEditorState extends State<DocumentEditor> {
  QuillController _controller = QuillController.basic();
  Timer? _debounce;
  bool _isLoading = true;
  bool _isSaving = false;
  String _lastSavedHtml = "";

  @override
  void initState() {
    super.initState();
    _loadContent();
  }

  Future<void> _loadContent() async {
    setState(() => _isLoading = true);
    try {
      final data = await apiService.getContenidoEditable(widget.documentoId);
      final rawHtml = data['contenido_html'] ?? "";
      
      // Conversión simplificada de HTML a Quill Delta
      // Se recomienda usar un paquete robusto como quill_html_converter en producción
      final doc = Document()
        ..insert(0, rawHtml.replaceAll(RegExp(r'<[^>]*>'), '')); // Fake strip HTML fallback
        
      _controller = QuillController(
        document: doc, 
        selection: const TextSelection.collapsed(offset: 0)
      );

      _lastSavedHtml = rawHtml;

      // Auto-guardado
      _controller.document.changes.listen((event) {
        _onContentChanged();
      });

    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _onContentChanged() {
    if (_debounce?.isActive ?? false) _debounce?.cancel();
    _debounce = Timer(const Duration(seconds: 2), () {
      _saveDocument();
    });
  }

  Future<void> _saveDocument() async {
    setState(() => _isSaving = true);
    try {
      // Conversión simplificada Quill Delta a HTML 
      final text = _controller.document.toPlainText();
      final htmlPayload = "<p>$text</p>"; // Fake wrap

      if (htmlPayload != _lastSavedHtml) {
        await apiService.guardarContenidoEditable(widget.documentoId, htmlPayload);
        _lastSavedHtml = htmlPayload;
      }
    } catch (e) {
      debugPrint("Error auto-guardando: $e");
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Column(
      children: [
        // Toolbar superior
        Container(
          color: Colors.grey.shade200,
          padding: const EdgeInsets.all(8.0),
          child: Row(
            children: [
              Expanded(
                child: Text("Editando: ${widget.nombre}", 
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)
                ),
              ),
              if (_isSaving) 
                const Text("Guardando...", style: TextStyle(color: Colors.grey, fontSize: 12)),
              if (!_isSaving) 
                const Text("Guardado", style: TextStyle(color: Colors.green, fontSize: 12)),
            ],
          ),
        ),
        
        // Quill Toolbar
        QuillToolbar.simple(
          configurations: QuillSimpleToolbarConfigurations(
            controller: _controller,
          ),
        ),
        
        // El editor per se
        Expanded(
          child: Container(
            color: Colors.white,
            padding: const EdgeInsets.all(16.0),
            child: QuillEditor.basic(
              configurations: QuillEditorConfigurations(
                controller: _controller,
                autoFocus: false,
                expands: true,
                padding: EdgeInsets.zero,
              ),
            ),
          ),
        )
      ],
    );
  }
}
