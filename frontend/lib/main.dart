import 'package:flutter/material.dart';
import 'package:abogacia_frontend/screens/splash_screen.dart';

void main() {
  runApp(const ZoteroLegalApp());
}

class ZoteroLegalApp extends StatelessWidget {
  const ZoteroLegalApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Gestor Legal Zotero',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blueGrey,
        scaffoldBackgroundColor: const Color(0xFFEBEBEB),
        iconTheme: const IconThemeData(color: Colors.blueGrey),
      ),
      home: const SplashScreen(), // Comienza verificando Auth
    );
  }
}
