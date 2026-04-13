import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:abogacia_frontend/services/api_service.dart';

class DocumentListPanel extends StatefulWidget {
  final int? collectionId;
  final Function(Map<String, dynamic>) onDocumentSelected;
  final Function(Map<String, dynamic>) onDocumentDoubleTapped;

  const DocumentListPanel({
    Key? key,
    this.collectionId,
    required this.onDocumentSelected,
    required this.onDocumentDoubleTapped,
  }) : super(key: key);

  @override
  State<DocumentListPanel> createState() => _DocumentListPanelState();
}

class _DocumentListPanelState extends State<DocumentListPanel> {
  List<dynamic> _documentos = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadDocuments();
  }

  @override
  void didUpdateWidget(covariant DocumentListPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.collectionId != widget.collectionId) {
      _loadDocuments();
    }
  }

  Future<void> _loadDocuments() async {
    setState(() => _isLoading = true);
    try {
      // Filtrado simplificado. Idealmente pasar filter a API.
      final docs = await apiService.getDocumentos();
      setState(() {
        _documentos = docs;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
    }
  }

  IconData _getIconForType(String? tipo) {
    switch(tipo?.toLowerCase()) {
      case 'pdf': return Icons.picture_as_pdf;
      case 'docx': 
      case 'doc': return Icons.description;
      case 'txt': return Icons.text_snippet;
      default: return Icons.article;
    }
  }

  Future<void> _subirArchivo() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['pdf', 'doc', 'docx', 'txt'],
      withData: true // Carga los bytes en memoria (necesario para Flutter Web/Windows)
    );

    if (result != null) {
      PlatformFile file = result.files.first;
      if (file.bytes != null) {
        setState(() => _isLoading = true);
        try {
          // TODO: Para un diseño más avanzado, casoId no debería ser hardcodeado como 1, 
          // sino ser determinado por la carpeta activa.
          await apiService.subirDocumento(file.name, file.bytes!, 1);
          await _loadDocuments(); // refrescamos
        } catch (e) {
          debugPrint(e.toString());
          setState(() => _isLoading = false);
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border(
          left: BorderSide(color: Colors.grey.shade300),
          right: BorderSide(color: Colors.grey.shade300),
        ),
      ),
      child: Column(
        children: [
          // Barra superior de acciones Zotero - Botón más verde
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
            color: Colors.grey.shade50,
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.add_circle, color: Colors.green),
                  tooltip: 'Añadir Archivo',
                  onPressed: _subirArchivo,
                ),
                // Aquí irían otros botones como Búsqueda Rápida...
              ]
            ),
          ),
          // Sub Toolbar for columns
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
            color: Colors.grey.shade100,
            child: const Row(
              children: [
                Expanded(child: Text("Título", style: TextStyle(fontWeight: FontWeight.bold))),
                SizedBox(width: 100, child: Text("Tipo", style: TextStyle(fontWeight: FontWeight.bold))),
              ],
            ),
          ),
          Expanded(
            child: _isLoading 
              ? const Center(child: CircularProgressIndicator())
              : ListView.builder(
                  itemCount: _documentos.length,
                  itemBuilder: (context, index) {
                    final doc = _documentos[index];
                    return InkWell(
                      onTap: () => widget.onDocumentSelected(doc),
                      onDoubleTap: () => widget.onDocumentDoubleTapped(doc),
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 8.0),
                        decoration: BoxDecoration(
                          border: Border(bottom: BorderSide(color: Colors.grey.shade200))
                        ),
                        child: Row(
                          children: [
                            Icon(_getIconForType(doc['tipo']), size: 20, color: Colors.blueGrey),
                            const SizedBox(width: 8),
                            Expanded(child: Text(doc['nombre'] ?? 'Desconocido', overflow: TextOverflow.ellipsis)),
                            SizedBox(width: 100, child: Text(doc['tipo']?.toUpperCase() ?? 'N/A')),
                          ],
                        ),
                      ),
                    );
                  },
                ),
          )
        ],
      ),
    );
  }
}
