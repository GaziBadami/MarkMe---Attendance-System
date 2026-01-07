import 'dart:convert';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:http/http.dart' as http;

class QRScanPage extends StatefulWidget {
  final String studentId;
  final String token;

  const QRScanPage({super.key, required this.studentId, required this.token});

  @override
  State<QRScanPage> createState() => _QRScanPageState();
}

class _QRScanPageState extends State<QRScanPage> {
  String? scannedData;
  bool isSubmitting = false;
  final MobileScannerController cameraController = MobileScannerController();

  Future<void> submitAttendance(String qrCodeId) async {
    setState(() {
      isSubmitting = true;
    });
    print(qrCodeId);
    print(widget.studentId);
    print(widget.token);
    final url = Uri.parse('https://mark-me-backend.onrender.com/attendance');
    try {
      // final response = await http.post(
      //   url,
      //   headers: {
      //     'Content-Type': 'application/json'
      //   },
      //   body: json.encode({
      //     'qr_code_id': qrCodeId,
      //     'student_id': widget.studentId,
      //   }),
      // );
      final response = await http.post(
        url,
        headers: {
          "Content-Type": "application/json",
        },
        body: json.encode({
          "qr_code_id": qrCodeId,
          "student_id": widget.studentId,
        }),
      );

      if (!mounted) return;

      setState(() {
        isSubmitting = false;
      });
      print('Status Code: ${response.statusCode}');
      print('Response Body: ${response.body}');
      if (response.statusCode == 200 || response.statusCode == 201) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text("✅ Attendance marked successfully!"),
            backgroundColor: Colors.green,
          ),
        );
        await Future.delayed(const Duration(seconds: 1));

        Navigator.pop(context);
        // Clear the scanned data to allow scanning again
        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            setState(() {
              scannedData = null;
            });
          }
        });
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text("Error: ${response.statusCode}"),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        isSubmitting = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Error: $e"),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    Map<String, dynamic>? qrDetails;
    try {
      if (scannedData != null) {
        qrDetails = json.decode(scannedData!);
      }
    } catch (_) {}

    return Scaffold(
      appBar: AppBar(title: const Text("Scan QR Code")),
      body: scannedData == null
          ? Column(
        children: [
          Expanded(
            flex: 4,
            child: MobileScanner(
              controller: cameraController,
              onDetect: (capture) {
                final List<Barcode> barcodes = capture.barcodes;
                for (final barcode in barcodes) {
                  if (barcode.displayValue != null &&
                      barcode.displayValue!.isNotEmpty) {
                    setState(() {
                      scannedData = barcode.displayValue;
                    });
                    break;
                  }
                }
              },
            ),
          ),
          const SizedBox(height: 20),
          const Text(
            "Point your camera at the QR code",
            style: TextStyle(fontSize: 16),
          ),
        ],
      )
          : Padding(
        padding: const EdgeInsets.all(16.0),
        child: qrDetails != null
            ? Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "QR Code Details",
              style: TextStyle(
                  fontSize: 22, fontWeight: FontWeight.bold),
            ),
            const Divider(),
            Text("Name: ${qrDetails['name'] ?? 'N/A'}"),
            Text(
                "Start Time: ${qrDetails['start_time'] ?? 'N/A'}"),
            Text("End Time: ${qrDetails['end_time'] ?? 'N/A'}"),
            Text(
                "QR Code ID: ${qrDetails['qr_code_id'] ?? 'N/A'}"),
            const SizedBox(height: 30),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: isSubmitting
                    ? null
                    : () {
                  submitAttendance(
                      qrDetails!['qr_code_id']);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFFFAA29),
                ),
                child: isSubmitting
                    ? const CircularProgressIndicator(
                    color: Colors.white)
                    : const Text(
                  "Mark Attendance",
                  style: TextStyle(
                      fontSize: 16, color: Colors.white),
                ),
              ),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              height: 50,
              child: ElevatedButton(
                onPressed: () {
                  setState(() {
                    scannedData = null;
                  });
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.grey,
                ),
                child: const Text(
                  "Scan Another",
                  style: TextStyle(
                      fontSize: 16, color: Colors.white),
                ),
              ),
            ),
          ],
        )
            : Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              "Invalid QR Data",
              style: TextStyle(fontSize: 18, color: Colors.red),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                setState(() {
                  scannedData = null;
                });
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFFFAA29),
              ),
              child: const Text("Scan Again"),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    cameraController.dispose();
    super.dispose();
  }
}