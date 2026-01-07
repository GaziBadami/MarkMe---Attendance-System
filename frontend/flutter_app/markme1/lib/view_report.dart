import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart'; // <-- ADDED

class ViewReportPage extends StatefulWidget {
  final String studentId;
  final String token;

  const ViewReportPage({
    super.key,
    required this.studentId,
    required this.token,
  });

  @override
  State<ViewReportPage> createState() => _ViewReportPageState();
}

class _ViewReportPageState extends State<ViewReportPage> {
  // FORMAT TIME FUNCTION
  String formatTime(String rawTime) {
    try {
      final parsed = DateTime.parse(rawTime);
      return DateFormat('hh:mm a').format(parsed); // 10:45 AM format
    } catch (e) {
      return rawTime; // return original if parsing fails
    }
  }

  Future<List<dynamic>> _fetchAttendance() async {
    final url = Uri.parse(
        "https://mark-me-backend.onrender.com/student/${widget.studentId}/attendance");

    print("--------------------------------------------------------");
    print("🔍 Fetching attendance from: $url");
    print("🔍 Token: ${widget.token}");
    print("--------------------------------------------------------");

    final response = await http.get(
      url,
      headers: {
        "Authorization": "Bearer ${widget.token}",
      },
    );

    print("🔍 Status Code: ${response.statusCode}");
    print("🔍 Body: ${response.body}");
    print("--------------------------------------------------------");

    if (response.statusCode == 200 || response.statusCode == 201) {
      return jsonDecode(response.body);
    } else {
      throw Exception("Failed to load attendance report");
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: const Color(0xFFFFB039),
        title: const Text(
          "Attendance Report",
          style: TextStyle(
            fontSize: 22,
            fontWeight: FontWeight.w600,
            color: Colors.white,
          ),
        ),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _fetchAttendance(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return const Center(
              child: Text(
                "Error loading report!",
                style: TextStyle(fontSize: 18, color: Colors.red),
              ),
            );
          }

          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(
              child: Text(
                "No attendance records found!",
                style: TextStyle(fontSize: 18),
              ),
            );
          }

          final data = snapshot.data!;

          return ListView.builder(
            padding: const EdgeInsets.all(12),
            itemCount: data.length,
            itemBuilder: (context, index) {
              final item = data[index];

              // format attendance time
              final String formattedTime = item['attendance_time'] != null
                  ? formatTime(item['attendance_time'])
                  : 'N/A';

              return Card(
                elevation: 3,
                margin: const EdgeInsets.only(bottom: 12),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "Date: ${item['day_label'] ?? 'N/A'}",
                        style: const TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text("Status: ${item['status']}"),
                      Text("Time: $formattedTime"), // <-- ONLY CHANGE
                      Text("QR Name: ${item['qr_code_name'] ?? 'N/A'}"),
                    ],
                  ),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
