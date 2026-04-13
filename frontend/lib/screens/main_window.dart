import 'package:flutter/material.dart';
import 'package:abogacia_frontend/screens/library_screen.dart';
import 'package:abogacia_frontend/widgets/document_editor.dart';

class MainWindow extends StatefulWidget {
  const MainWindow({Key? key}) : super(key: key);

  @override
  State<MainWindow> createState() => _MainWindowState();
}

class DocumentTab {
  final int id;
  final String title;
  
  DocumentTab({required this.id, required this.title});
}

class _MainWindowState extends State<MainWindow> {
  // Lista de pestañas abiertas. La pestaña 0 es siempre la Biblioteca.
  List<DocumentTab> _openTabs = [];
  int _currentIndex = 0;

  void _openDocumentInNewTab(int id, String title) {
    // Si ya está abierta, hacer foco en ella
    int existingIndex = _openTabs.indexWhere((t) => t.id == id);
    if (existingIndex != -1) {
      setState(() {
        _currentIndex = existingIndex + 1; // +1 porque la 0 es la biblioteca
      });
      return;
    }

    // Agregar nueva pestaña
    setState(() {
      _openTabs.add(DocumentTab(id: id, title: title));
      _currentIndex = _openTabs.length; // Foco en la nueva (que será la última)
    });
  }

  void _closeTab(int index) {
    setState(() {
      _openTabs.removeAt(index - 1); // -1 porque el offset 0 es la biblioteca
      if (_currentIndex >= index) {
        // Reducir currentIndex si se cerró la activa o una anterior
        _currentIndex--;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(40.0),
        child: Container(
          color: Colors.grey.shade300,
          child: Row(
            children: [
              // Barra de Pestañas (Tab Bar) parecida a Zotero o Chrome
              _buildTab(
                title: "Mi Biblioteca",
                icon: Icons.library_books,
                isActive: _currentIndex == 0,
                onTap: () => setState(() => _currentIndex = 0),
                closable: false,
              ),
              Expanded(
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _openTabs.length,
                  itemBuilder: (context, i) {
                    final tabIndex = i + 1;
                    final tab = _openTabs[i];
                    return _buildTab(
                      title: tab.title,
                      icon: Icons.article,
                      isActive: _currentIndex == tabIndex,
                      onTap: () => setState(() => _currentIndex = tabIndex),
                      closable: true,
                      onClose: () => _closeTab(tabIndex),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    // Si el index es 0, mostramos la Biblioteca tradicional de 3 paneles
    if (_currentIndex == 0) {
      return LibraryScreen(
        onOpenDocumentTab: (int id, String title) {
          _openDocumentInNewTab(id, title);
        },
      );
    }

    // Si es > 0, mostramos el editor para el documento abierto
    final activeTab = _openTabs[_currentIndex - 1];
    return DocumentEditor(
      key: ValueKey(activeTab.id), // Importante para resetear estado si cambia rápido
      documentoId: activeTab.id,
      nombre: activeTab.title,
    );
  }

  Widget _buildTab({
    required String title,
    required IconData icon,
    required bool isActive,
    required VoidCallback onTap,
    required bool closable,
    VoidCallback? onClose,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 0),
        decoration: BoxDecoration(
          color: isActive ? Colors.white : Colors.grey.shade300,
          border: Border(
            right: BorderSide(color: Colors.grey.shade400, width: 1),
            top: BorderSide(color: isActive ? Colors.blue : Colors.transparent, width: 3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: isActive ? Colors.blueGrey.shade700 : Colors.grey.shade600),
            const SizedBox(width: 8),
            ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 150),
              child: Text(
                title,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                  color: isActive ? Colors.black87 : Colors.black54,
                ),
              ),
            ),
            if (closable) ...[
              const SizedBox(width: 8),
              InkWell(
                onTap: onClose,
                child: Container(
                  padding: const EdgeInsets.all(2),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                    color: Colors.transparent,
                  ),
                  child: Icon(Icons.close, size: 14, color: Colors.grey.shade700),
                ),
              )
            ]
          ],
        ),
      ),
    );
  }
}
