import 'package:flutter/material.dart';
import 'package:multi_split_view/multi_split_view.dart';
import 'package:abogacia_frontend/widgets/collections_panel.dart';
import 'package:abogacia_frontend/widgets/document_list_panel.dart';
import 'package:abogacia_frontend/widgets/document_detail_panel.dart';

class LibraryScreen extends StatefulWidget {
  final Function(int, String)? onOpenDocumentTab;

  const LibraryScreen({Key? key, this.onOpenDocumentTab}) : super(key: key);

  @override
  State<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends State<LibraryScreen> {
  // Estado básico de selección
  int? _selectedCollectionId;
  Map<String, dynamic>? _selectedDocument;

  void _openInNewTab(Map<String, dynamic> doc) {
    if (widget.onOpenDocumentTab != null) {
      widget.onOpenDocumentTab!(doc['id'], doc['nombre'] ?? 'Sin título');
    }
  }

  @override
  Widget build(BuildContext context) {
    // Definimos los tres paneles
    Widget leftPanel = CollectionsPanel(
      onCollectionSelected: (id) {
        setState(() {
          _selectedCollectionId = id;
          _selectedDocument = null; // Reset
        });
      },
    );

    Widget centerPanel = DocumentListPanel(
      collectionId: _selectedCollectionId,
      onDocumentSelected: (doc) {
        setState(() {
          _selectedDocument = doc;
        });
      },
      onDocumentDoubleTapped: (doc) {
         _openInNewTab(doc);
      }
    );

    Widget rightPanel;
    if (_selectedDocument == null) {
      rightPanel = const Center(child: Text("Seleccione un documento para ver sus detalles"));
    } else {
      // Panel de Metadatos SIEMPRE en la derecha en la librería
      rightPanel = DocumentDetailPanel(
        document: _selectedDocument!,
        onEditRequested: () {
          _openInNewTab(_selectedDocument!);
        },
      );
    }

    final splitView = MultiSplitView(
      children: [leftPanel, centerPanel, rightPanel],
      initialAreas: [
        Area(weight: 0.20), // 20% Colecciones
        Area(weight: 0.35), // 35% Lista de Documentos
        Area(weight: 0.45), // 45% Visor / Editor
      ],
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('Gestor Legal - Abogacía', style: TextStyle(fontSize: 16)),
        actions: [
          IconButton(
            icon: const Icon(Icons.sync),
            tooltip: 'Sincronizar',
            onPressed: () {},
          ),
        ],
      ),
      body: MultiSplitViewTheme(
        data: MultiSplitViewThemeData(
          dividerPainter: DividerPainters.grooved1(
            color: Colors.grey.shade300,
            highlightedColor: Colors.blueGrey,
          ),
        ),
        child: splitView,
      ),
    );
  }
}
