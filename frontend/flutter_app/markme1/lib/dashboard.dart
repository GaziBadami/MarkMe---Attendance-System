import 'package:flutter/material.dart';
import 'login_screen.dart';
import 'qr_scan_page.dart';
import 'view_report.dart';

class DashboardScreen extends StatelessWidget {
  final Map<String, dynamic> userData;
  final String token;

  const DashboardScreen({
    super.key,
    required this.userData,
    this.token = '',
  });

  Widget buildDetailRow(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text("$label: $value", style: const TextStyle(fontSize: 16)),
        const Divider(thickness: 1, color: Colors.orangeAccent),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("MarkMe"),
        centerTitle: false,
        elevation: 4,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              Navigator.pushReplacement(
                context,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "Welcome, ${userData['first_name']} ${userData['last_name']} 👋",
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            // Profile Card
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              color: Colors.orange[50],
              elevation: 6,
              shadowColor: Colors.orangeAccent,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    buildDetailRow("Enrollment No", userData['enrollment_no']),
                    buildDetailRow("Course", userData['course']),
                    buildDetailRow("Email", userData['email']),
                    buildDetailRow("Phone", userData['phone_number']),
                    buildDetailRow("Div", userData['div']),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Buttons Row
            Row(
              children: [
                // Scan QR Button
                Expanded(
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => QRScanPage(
                            studentId: userData['id'],
                            token: token,
                          ),
                        ),
                      );
                    },
                    child: Card(
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                      color: Colors.orange[100],
                      elevation: 4,
                      child: SizedBox(
                        height: 120,
                        child: Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: const [
                              Icon(Icons.qr_code_scanner,
                                  size: 40, color: Colors.orange),
                              SizedBox(height: 8),
                              Text(
                                "Scan QR",
                                style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),

                const SizedBox(width: 16),

                // View Report Button
                Expanded(
                  child: GestureDetector(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ViewReportPage(
                            studentId: userData['id'],
                            token: token,
                          ),
                        ),
                      );
                    },
                    child: Card(
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                      color: Colors.orange[100],
                      elevation: 4,
                      child: SizedBox(
                        height: 120,
                        child: Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: const [
                              Icon(Icons.insert_drive_file,
                                  size: 40, color: Colors.orange),
                              SizedBox(height: 8),
                              Text(
                                "View Report",
                                style: TextStyle(
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
