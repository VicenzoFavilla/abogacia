import 'package:flutter/material.dart';
import 'package:abogacia_frontend/services/api_service.dart';

class CollectionsPanel extends StatefulWidget {
  final Function(int?) onCollectionSelected;

  const CollectionsPanel({Key? key, required this.onCollectionSelected}) : super(key: key);

  @override
  State<CollectionsPanel> createState() => _CollectionsPanelState();
}

class _CollectionsPanelState extends State<CollectionsPanel> {
  List<dynamic> _colecciones = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadCollections();
  }

  Future<void> _loadCollections() async {
    try {
      final cols = await apiService.getColecciones();
      setState(() {
        _colecciones = cols;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      // Failsafe in dev if backend not up
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    return Container(
      color: Colors.white,
      child: ListView(
        children: [
          ListTile(
            leading: const Icon(Icons.library_books, color: Colors.blueGrey),
            title: const Text('Mi Biblioteca', style: TextStyle(fontWeight: FontWeight.bold)),
            onTap: () => widget.onCollectionSelected(null),
          ),
          const Divider(),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
            child: Text('Colecciones', style: TextStyle(color: Colors.grey, fontSize: 12, fontWeight: FontWeight.bold)),
          ),
          ..._colecciones.map((col) => _buildCollectionItem(col)).toList(),
          const Divider(),
          ListTile(
            leading: const Icon(Icons.add, color: Colors.grey),
            title: const Text('Nueva Colección', style: TextStyle(color: Colors.grey)),
            onTap: _mostrarDialogoNuevaColeccion,
          ),
        ],
      ),
    );
  }

  void _mostrarDialogoNuevaColeccion() {
    final TextEditingController _controller = TextEditingController();
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text("Nueva Colección"),
          content: TextField(
            controller: _controller,
            decoration: const InputDecoration(hintText: "Nombre de la carpeta..."),
            autofocus: true,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text("Cancelar"),
            ),
            ElevatedButton(
              onPressed: () async {
                if (_controller.text.trim().isNotEmpty) {
                  Navigator.pop(context); // Cerramos modalidad
                  setState(() => _isLoading = true);
                  await apiService.crearColeccion(_controller.text.trim());
                  _loadCollections(); // Recarga la lista
                }
              },
              child: const Text("Crear"),
            ),
          ],
        );
      }
    );
  }

  Widget _buildCollectionItem(Map<String, dynamic> col) {
    // Para simplificar, este es un Tile simple. 
    // Para hijos reales usaríamos un ExpansionTile
    return ListTile(
      leading: const Icon(Icons.folder, color: Colors.amber),
      title: Text(col['nombre'] ?? 'Sin nombre'),
      onTap: () => widget.onCollectionSelected(col['id']),
    );
  }
}
