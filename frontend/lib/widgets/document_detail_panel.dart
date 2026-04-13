import 'package:flutter/material.dart';
import 'package:abogacia_frontend/services/api_service.dart';

class DocumentDetailPanel extends StatefulWidget {
  final Map<String, dynamic> document;
  final VoidCallback onEditRequested;

  const DocumentDetailPanel({
    Key? key, 
    required this.document,
    required this.onEditRequested,
  }) : super(key: key);

  @override
  State<DocumentDetailPanel> createState() => _DocumentDetailPanelState();
}

class _DocumentDetailPanelState extends State<DocumentDetailPanel> {
  late TextEditingController _nombreCtrl;
  late TextEditingController _tipoCtrl;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _initControllers();
  }

  @override
  void didUpdateWidget(covariant DocumentDetailPanel oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.document['id'] != widget.document['id']) {
      _initControllers();
    }
  }

  void _initControllers() {
    _nombreCtrl = TextEditingController(text: widget.document['nombre'] ?? '');
    _tipoCtrl = TextEditingController(text: widget.document['tipo'] ?? '');
  }

  Future<void> _guardarCambios() async {
    setState(() => _isSaving = true);
    try {
      await apiService.actualizarDocumento(
        widget.document['id'], 
        _nombreCtrl.text, 
        _tipoCtrl.text
      );
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Guardado'), duration: Duration(seconds: 1)));
    } catch (e) {
      debugPrint(e.toString());
    } finally {
      setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    // Si el documento es doc/docx o txt se puede editar
    final isEditable = ['docx', 'doc', 'txt'].contains(widget.document['tipo']?.toLowerCase());

    return Container(
      color: Colors.grey.shade50,
      child: DefaultTabController(
        length: 3,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const TabBar(
              labelColor: Colors.blueGrey,
              indicatorColor: Colors.blueGrey,
              tabs: [
                Tab(text: "Info"),
                Tab(text: "Notas"),
                Tab(text: "Etiquetas"),
              ],
            ),
            Expanded(
              child: TabBarView(
                children: [
                  _buildInfoTab(isEditable),
                  const Center(child: Text("Sección de notas")),
                  const Center(child: Text("Sección de etiquetas")),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoTab(bool isEditable) {
    return ListView(
      padding: const EdgeInsets.all(16.0),
      children: [
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: TextField(
                controller: _nombreCtrl,
                style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                decoration: const InputDecoration(border: InputBorder.none, hintText: 'Título del documento'),
                onSubmitted: (_) => _guardarCambios(),
              ),
            ),
            if (isEditable)
              ElevatedButton.icon(
                onPressed: widget.onEditRequested,
                icon: const Icon(Icons.edit, size: 16),
                label: const Text("Editar Contenido"),
              ),
          ],
        ),
        const SizedBox(height: 16),
        _buildEditableRow("Tipo de Item", _tipoCtrl),
        _buildMetadataRow("Fecha de subida", widget.document['fecha_subida'] ?? '-'),
        const Divider(height: 32),
        // Placeholder para Metadatos Legales
        const Text("Metadatos Legales (En Desarrollo)", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blueGrey)),
        const SizedBox(height: 8),
        _buildMetadataRow("Nro. Expediente", "Sin procesar"),
        _buildMetadataRow("Tribunal", "Sin procesar"),
        _buildMetadataRow("Partes", "Sin procesar"),
        const SizedBox(height: 32),
        Align(
          alignment: Alignment.centerRight,
          child: ElevatedButton(
            onPressed: _isSaving ? null : _guardarCambios,
            child: _isSaving 
              ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)) 
              : const Text("Guardar Metadatos"),
          )
        )
      ],
    );
  }

  Widget _buildEditableRow(String label, TextEditingController controller) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          SizedBox(
            width: 120,
            child: Text(label, style: const TextStyle(color: Colors.grey, fontWeight: FontWeight.w500)),
          ),
          Expanded(
            child: TextField(
              controller: controller,
              decoration: const InputDecoration(isDense: true, border: OutlineInputBorder()),
              onSubmitted: (_) => _guardarCambios(),
            )
          ),
        ],
      ),
    );
  }

  Widget _buildMetadataRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 120,
            child: Text(label, style: const TextStyle(color: Colors.grey, fontWeight: FontWeight.w500)),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
