import 'package:flutter/material.dart';
import 'package:abogacia_frontend/screens/main_window.dart';
import 'package:abogacia_frontend/services/api_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _emailCtrl = TextEditingController(text: "admin@abogacia.com");
  final TextEditingController _passCtrl = TextEditingController(text: "admin");
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _attemptLogin() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final success = await apiService.login(_emailCtrl.text.trim(), _passCtrl.text);

      setState(() {
        _isLoading = false;
      });

      if (success && mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const MainWindow())
        );
      }
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString().replaceAll("Exception: ", "");
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFEBEBEB), // Fondo estilo Zotero
      body: Center(
        child: Container(
          width: 400,
          padding: const EdgeInsets.all(32.0),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8.0),
            boxShadow: const [
              BoxShadow(
                color: Colors.black12,
                blurRadius: 10.0,
                offset: Offset(0, 4),
              )
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Icon(Icons.account_balance, size: 64, color: Colors.blueGrey),
              const SizedBox(height: 16),
              const Text(
                'Gestor Legal Zotero',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.blueGrey),
              ),
              const SizedBox(height: 32),
              if (_errorMessage != null)
                Container(
                  padding: const EdgeInsets.all(8.0),
                  margin: const EdgeInsets.only(bottom: 16.0),
                  color: Colors.red.shade100,
                  child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
                ),
              TextField(
                controller: _emailCtrl,
                decoration: const InputDecoration(
                  labelText: 'Correo Electrónico',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.email),
                ),
                keyboardType: TextInputType.emailAddress,
                onSubmitted: (_) => _attemptLogin(),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: _passCtrl,
                decoration: const InputDecoration(
                  labelText: 'Contraseña',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.lock),
                ),
                obscureText: true,
                onSubmitted: (_) => _attemptLogin(),
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.blueGrey,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                onPressed: _isLoading ? null : _attemptLogin,
                child: _isLoading 
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Text('Iniciar Sesión', style: TextStyle(fontSize: 16)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
