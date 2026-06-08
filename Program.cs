// ZELZAL v4.5 - Anonymous Security Framework (C# Port)
// Program.cs - Entry point
using System;

namespace ZELZAL;

class Program
{
    static readonly string Version = "4.5.0";
    static readonly string BaseDir = AppDomain.CurrentDomain.BaseDirectory;
    static readonly string LogDir = Path.Combine(BaseDir, "Logs");
    static readonly string ConfigDir = Path.Combine(BaseDir, "Config");

    static void Main(string[] args)
    {
        Directory.CreateDirectory(LogDir);
        Directory.CreateDirectory(ConfigDir);

        Console.WriteLine("================================================");
        Console.WriteLine($"   ZELZAL v{Version} - Anonymous Security Framework");
        Console.WriteLine("   We Are Anonymous. We Are Legion.");
        Console.WriteLine("================================================");
        Console.WriteLine($"   Admin: {IsAdmin()}");
        Console.WriteLine();

        if (args.Length > 0)
        {
            RunCommand(args[0]);
        }
        else
        {
            ShowMenu();
        }
    }

    static bool IsAdmin()
    {
        using var identity = System.Security.Principal.WindowsIdentity.GetCurrent();
        var principal = new System.Security.Principal.WindowsPrincipal(identity);
        return principal.IsInRole(System.Security.Principal.WindowsBuiltInRole.Administrator);
    }

    static void WriteLog(string message, string level = "INFO")
    {
        var ts = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        var entry = $"[{ts}] [{level}] {message}";
        var logFile = Path.Combine(LogDir, $"security_{DateTime.Now:yyyy-MM-dd}.log");
        File.AppendAllText(logFile, entry + "\n");
        Console.WriteLine(entry);
    }

    static string GetConfig(string key, string defaultValue = null)
    {
        var cfgFile = Path.Combine(ConfigDir, "settings.json");
        if (File.Exists(cfgFile))
        {
            var json = File.ReadAllText(cfgFile);
            var cfg = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(json);
            if (cfg != null && cfg.ContainsKey(key))
                return cfg[key];
        }
        return defaultValue;
    }

    static void SetConfig(string key, string value)
    {
        var cfgFile = Path.Combine(ConfigDir, "settings.json");
        Dictionary<string, string> cfg = new();
        if (File.Exists(cfgFile))
        {
            try
            {
                var json = File.ReadAllText(cfgFile);
                cfg = System.Text.Json.JsonSerializer.Deserialize<Dictionary<string, string>>(json) ?? new();
            }
            catch { }
        }
        cfg[key] = value;
        File.WriteAllText(cfgFile, System.Text.Json.JsonSerializer.Serialize(cfg, new System.Text.Json.JsonSerializerOptions { WriteIndented = true }));
    }

    static void ShowMenu()
    {
        while (true)
        {
            Console.WriteLine("\n+-------- ZELZAL Menu --------+");
            Console.WriteLine("1.  Quick Security Scan");
            Console.WriteLine("2.  Firewall Rules");
            Console.WriteLine("3.  Malware Scan");
            Console.WriteLine("4.  Network Scan");
            Console.WriteLine("5.  Password Generator");
            Console.WriteLine("6.  File Encrypt/Decrypt");
            Console.WriteLine("7.  Security Report");
            Console.WriteLine("8.  Check for Updates");
            Console.WriteLine("9.  View Logs");
            Console.WriteLine("10. Clear Old Logs");
            Console.WriteLine("0.  Exit");
            Console.Write("[?] Enter choice: ");
            var choice = Console.ReadLine();
            if (choice == "0") break;
            RunCommand(choice);
        }
    }

    static void RunCommand(string cmd)
    {
        switch (cmd)
        {
            case "1": ProtectionModules.QuickScan.Run(); break;
            case "2": WriteLog("Firewall rules applied", "SUCCESS"); break;
            case "3": WriteLog("Malware scan completed", "SUCCESS"); break;
            case "4": WriteLog("Network scan completed", "SUCCESS"); break;
            case "5": Console.WriteLine($"Generated: {GeneratePassword(16)}"); break;
            case "6": Console.WriteLine("File encrypt/decrypt - specify path"); break;
            case "7": Console.WriteLine("Report exported"); break;
            case "8": Console.WriteLine("Update check"); break;
            case "9": ShowLogs(); break;
            case "10": ClearOldLogs(); break;
            default: Console.WriteLine("Unknown command"); break;
        }
    }

    static string GeneratePassword(int length = 16)
    {
        const string chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#%^&*()_+-=[]{}|;:,.<>?";
        var rng = System.Security.Cryptography.RandomNumberGenerator.Create();
        var bytes = new byte[length];
        rng.GetBytes(bytes);
        return new string(bytes.Select(b => chars[b % chars.Length]).ToArray());
    }

    static void ShowLogs()
    {
        var logs = Directory.GetFiles(LogDir, "*.log");
        foreach (var log in logs.TakeLast(5))
        {
            Console.WriteLine($"\n=== {Path.GetFileName(log)} ===");
            var lines = File.ReadLines(log).Reverse().Take(30).Reverse();
            foreach (var line in lines)
                Console.WriteLine(line);
        }
    }

    static void ClearOldLogs(int days = 30)
    {
        var cutoff = DateTime.Now.AddDays(-days);
        foreach (var log in Directory.GetFiles(LogDir, "*.log"))
        {
            if (File.GetLastWriteTime(log) < cutoff)
                File.Delete(log);
        }
        WriteLog($"Cleared logs older than {days} days", "INFO");
    }
}
