import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:abogacia_frontend/screens/login_screen.dart';
import 'package:abogacia_frontend/screens/main_window.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    // Breve pausa para que se renderice el logo inicial de splash
    await Future.delayed(const Duration(milliseconds: 500));
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');

    if (mounted) {
      if (token != null && token.isNotEmpty) {
        // Logueado, vamos al MainWindow
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const MainWindow())
        );
      } else {
        // No logueado, vamos al LoginScreen
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const LoginScreen())
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFEBEBEB),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(Icons.account_balance, size: 80, color: Colors.blueGrey),
            SizedBox(height: 24),
            CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}
