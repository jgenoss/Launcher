// LauncherUpdater/Program.cs
using System;
using System.IO;
using System.Net;
using System.Threading;
using System.Diagnostics;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length != 3) return;

        try
        {
            string url = args[0];
            string launcherPath = args[1];
            string fileName = args[2];
            string selfPath = Process.GetCurrentProcess().MainModule.FileName;

            Thread.Sleep(2000);

            using (var client = new WebClient())
            {
                client.DownloadFile($"{url}/launcher_updates/{fileName}", "temp_launcher.exe");
            }

            if (File.Exists(launcherPath)) File.Delete(launcherPath);
            File.Move("temp_launcher.exe", launcherPath);

            string batchPath = Path.Combine(Path.GetTempPath(), "cleanup.bat");
            string batchContent =
                "@echo off\r\n" +
                "timeout /t 1 /nobreak > nul\r\n" +
                $"del \"{selfPath}\"\r\n" +
                $"rd /s /q \"{Path.Combine(Path.GetDirectoryName(launcherPath), "launcher_updates")}\"\r\n" +
                $"rd /s /q \"{Path.Combine(Path.GetDirectoryName(launcherPath), "updates")}\"\r\n" +
                $"start \"\" \"{launcherPath}\"\r\n" +
                "del \"%~f0\"";

            File.WriteAllText(batchPath, batchContent);
            Process.Start(batchPath);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
            Thread.Sleep(5000);
        }
    }
}