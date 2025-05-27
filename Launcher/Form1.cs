using System;
using System.IO;
//using System.IO.Compression;
using System.Linq;
using System.Net;
using Newtonsoft.Json;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Diagnostics;
using Ionic.Zip;
using System.Text;
using CefSharp;
using CefSharp.WinForms;

namespace Launcher
{
    public partial class Form1 : Form
    {
        public int Versions;
        public byte[] Header_lccnct;
        public byte[] Header_sl;
        private const string ConfigFile = "./config.json";
        private const string UpdateFile = "update.json";
        private const string UpdatesPath = "updates/";
        private string Urls = "http://172.86.80.197/Launcher/";
        private string UrbBanner = "http://172.86.80.197/Launcher/banner.html";
        public class LauncherVersionInfo
        {
            public string version { get; set; }
            public string file_name { get; set; }
        }
        public Form1()
        {

            InitializeComponent();

            Urls = readdtafile("lccnct.dta");
            UrbBanner = $"{Urls}banner.html";

            btnStart.Enabled = false;

            if (Directory.Exists(UpdatesPath))
            {
                try
                {
                    DeleteDirectory(UpdatesPath);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error al eliminar carpeta updates: {ex.Message}");
                }
            }
            // Crear carpeta de actualizaciones si no existe

            chromiumWebBrowser1.Load(UrbBanner);
            //progressBarDownload.Visible = false;
            //progressBarExtract.Visible = false;
            lblExtract.Text = "100%";
            lblDownload.Text = "100%";
            // Verificar actualizaciones al cargar el formulario
            // Modificar el evento Load para incluir la verificación del launcher
            this.Load += async (s, e) =>
            {
                // Primero verificar actualización del launcher
                await CheckLauncherUpdate();
                // Luego verificar actualizaciones del juego
                await VerifyAndUpdateAsync();
            };
        }

        /// <summary>
        /// Verifica y aplica actualizaciones al iniciar el lanzador.
        /// </summary>
        public string readdtafile(string FileName)
        {
            ASCIIEncoding asciiencoding = new ASCIIEncoding();
            BinaryReader binaryReader = new BinaryReader(File.Open(FileName, FileMode.Open));
            int num = 19;
            int num2 = (int)binaryReader.BaseStream.Length - num;
            byte[] array = binaryReader.ReadBytes(num);
            if (Path.GetFileName(FileName) == "lccnct.dta")
            {
                Header_lccnct = array;
            }
            if (Path.GetFileName(FileName) == "sl.dta")
            {
                Header_sl = array;
            }
            byte[] array2 = binaryReader.ReadBytes(num2);
            binaryReader.Close();
            byte b = array[10];
            for (int i = 0; i < num2; i++)
            {
                byte[] array3 = array2;
                int num3 = i;
                array3[num3] -= b;
                b += array2[i];
            }
            return asciiencoding.GetString(array2);
        }
        private async Task CheckLauncherUpdate()
        {
            try
            {
                using (var client = new WebClient())
                {
                    var json = await client.DownloadStringTaskAsync($"{Urls}launcher_update.json");
                    var info = JsonConvert.DeserializeObject<LauncherVersionInfo>(json);

                    if (Version.Parse(info.version) > Version.Parse(Application.ProductVersion))
                    {
                        

                        // Descargar LauncherUpdater.exe
                        string updaterPath = Path.Combine(Application.StartupPath, "LauncherUpdater.exe");
                        await client.DownloadFileTaskAsync($"{Urls}LauncherUpdater.exe", updaterPath);

                        if (MessageBox.Show("Hay una actualización disponible. ¿Desea actualizar?",
                            "Actualización", MessageBoxButtons.YesNo) == DialogResult.Yes)
                        {
                            Process.Start(updaterPath,
                                $"\"{Urls}\" \"{Application.ExecutablePath}\" \"{info.file_name}\"");
                            Application.Exit();
                        }
                        else
                        {
                            // Si el usuario cancela, eliminar el updater
                            if (File.Exists(updaterPath))
                            {
                                File.Delete(updaterPath);
                            }
                        }
                    }
                    else
                    {
                        btnStart.Enabled = true;
                    }
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error al verificar actualización: {ex.Message}");
                btnStart.Enabled = false;
            }
        }
        private void DeleteDirectory(string path)
        {
            try
            {
                foreach (string file in Directory.GetFiles(path))
                {
                    File.SetAttributes(file, FileAttributes.Normal);
                    File.Delete(file);
                }

                foreach (string dir in Directory.GetDirectories(path))
                {
                    DeleteDirectory(dir);
                }

                Directory.Delete(path, true);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error al eliminar directorio: {ex.Message}");
            }
        }
        public async Task VerifyAndUpdateAsync()
        {
            try
            {
                lblStatus.Text = "Cargando configuración...";
                await Task.Delay(10);
                var config = LoadConfig();

                lblStatus.Text = "Obteniendo datos del servidor...";
                await Task.Delay(10);
                var serverData = await FetchServerDataAsync();
                lblLatestVersion.Text = $"{serverData.latest_version}";

                if (IsUpdateRequired(config.InstalledVersion, serverData.latest_version))
                {
                    // Crear la carpeta updates solo si hay actualización
                    if (!Directory.Exists(UpdatesPath))
                    {
                        Directory.CreateDirectory(UpdatesPath);
                    }

                    lblStatus.Text = $"Nueva versión disponible: {serverData.latest_version}";
                    await Task.Delay(10);
                    await ApplyUpdatesAsync(config.InstalledVersion, serverData);
                    UpdateConfig(config, serverData.latest_version);

                    // Eliminar carpeta updates después de actualizar
                    

                    lblStatus.Text = "Juego actualizado correctamente.";
                    btnStart.Enabled = true;
                    await Task.Delay(10);
                }
                else
                {
                    lblStatus.Text = "El juego ya está actualizado.";
                    btnStart.Enabled = true;
                    progressBarDownload.Value = 100;
                    progressBarExtract.Value = 100;
                    await Task.Delay(10);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error: {ex.Message}");
                Application.Exit();
            }
        }


        private Config LoadConfig()
        {
            if (!File.Exists(ConfigFile))
            {
                MessageBox.Show("El archivo config.json no existe, creando uno nuevo con la versión 1.0.0.0.");
                var defaultConfig = new Config { InstalledVersion = "1.0.0.0" };
                File.WriteAllText(ConfigFile, JsonConvert.SerializeObject(defaultConfig));
                return defaultConfig;

            }

            var configJson = File.ReadAllText(ConfigFile);
            if (string.IsNullOrWhiteSpace(configJson))
            {
                MessageBox.Show("El archivo config.json está vacío.");
                var defaultConfig = new Config { InstalledVersion = "1.0.0.0" };
                File.WriteAllText(ConfigFile, JsonConvert.SerializeObject(defaultConfig));
                return defaultConfig;
            }

            var config = JsonConvert.DeserializeObject<Config>(configJson);
            //MessageBox.Show($"Versión instalada cargada: {config.InstalledVersion}");  // Aquí verificamos el valor
            return config;
        }



        private async Task<ServerData> FetchServerDataAsync()
        {
            using (var client = new WebClient())
            {
                try
                {
                    var json = await client.DownloadStringTaskAsync($"{Urls}{UpdateFile}");

                    // Agregar un mensaje de depuración para ver la respuesta del servidor
                    //MessageBox.Show($"Respuesta del servidor: {json}");

                    if (string.IsNullOrWhiteSpace(json))
                    {
                        throw new InvalidOperationException("La respuesta del servidor está vacía.");
                    }
                    var serverData = JsonConvert.DeserializeObject<ServerData>(json);
                    if (serverData == null || string.IsNullOrWhiteSpace(serverData.latest_version))
                    {
                        throw new InvalidOperationException("No se recibió la versión más reciente del servidor.");
                    }

                    return serverData;
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error al obtener los datos del servidor: {ex.Message}");
                    throw; // Propaga la excepción para que sea manejada en el bloque superior
                }
            }
        }

        private bool IsUpdateRequired(string installedVersion, string latestVersion)
        {
            // Verifica los valores antes de la comparación
            //MessageBox.Show($"Comparando versiones: {installedVersion} vs {latestVersion}");

            if (string.IsNullOrWhiteSpace(installedVersion) || string.IsNullOrWhiteSpace(latestVersion))
            {
                MessageBox.Show("Una de las versiones es nula o vacía.");
                return false;
            }

            try
            {
                return Version.Parse(installedVersion) < Version.Parse(latestVersion);
            }
            catch (FormatException ex)
            {
                throw new Exception($"Error al comparar versiones: {ex.Message}");
            }
        }
        private async Task ApplyUpdatesAsync(string installedVersion, ServerData serverData)
        {
            if (serverData?.updates == null || serverData.updates.Length == 0)
            {
                throw new InvalidOperationException("No hay actualizaciones disponibles en el servidor.");
            }

            var updatesToApply = serverData.updates
                .Where(update => Version.Parse(GetVersionFromUpdate(update)) > Version.Parse(installedVersion))
                .OrderBy(update => Version.Parse(GetVersionFromUpdate(update)));

            foreach (var update in updatesToApply)
            {
                lblDownload.Text = $"Descargando {update}...";
                await DownloadUpdateFileAsync(update);

                lblStatus.Text = $"Aplicando {update}...";
                ExtractUpdate(update);
            }
        }


        // Método para descargar actualizaciones
        private async Task DownloadUpdateFileAsync(string update)
        {
            using (var client = new WebClient())
            {
                // Configurar la barra de progreso de la descarga
                var updateUrl = $"{Urls}{UpdatesPath}{update}";  // Ahora descargamos desde 'http://localhost/launcher/updates/{update}'
                var localPath = Path.Combine(UpdatesPath, update);

                progressBarDownload.Value = 0; // Reiniciar progreso
                progressBarDownload.Visible = true; // Hacer visible la barra de progreso de descarga
                lblDownload.Visible = true;

                // Usar el evento para monitorear el progreso de la descarga
                client.DownloadProgressChanged += async (sender, e) =>
                {
                    // Actualizar el progreso en la barra
                    progressBarDownload.Value = e.ProgressPercentage;
                    lblDownload.Text = $"Descargando... {e.ProgressPercentage}%";
                    await Task.Delay(10);
                };
                try
                {
                    // Descargar el archivo y reemplazar si ya existe
                    await client.DownloadFileTaskAsync(updateUrl, localPath);
                    progressBarDownload.Value = 100; // Completar la barra de progreso
                    lblDownload.Text = "¡Descarga completada!";
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error al descargar el archivo {update}: {ex.Message}");
                }
            }
        }
        private async void ExtractUpdate(string update)
        {
            // Configurar la barra de progreso de extracción
            progressBarExtract.Value = 0; // Reiniciar progreso
            progressBarExtract.Visible = true; // Hacer visible la barra de progreso de extracción

            var localPath = Path.Combine(UpdatesPath, update); // Ruta al archivo ZIP
            var extractPath = "./"; // Ruta donde extraeremos el contenido

            try
            {
                // Abrir el archivo ZIP
                using (ZipFile archive = ZipFile.Read(localPath))
                {
                    int totalFiles = archive.Entries.Count;  // Número total de archivos en el archivo ZIP
                    int extractedFiles = 0;  // Contador de archivos extraídos

                    // Iterar sobre cada archivo en el ZIP
                    foreach (var entry in archive.Entries)
                    {
                        var destinationPath = Path.Combine(extractPath, entry.FileName);

                        // Verificar si el archivo ya existe y reemplazarlo
                        if (File.Exists(destinationPath))
                        {
                            File.Delete(destinationPath);  // Eliminar el archivo existente
                        }

                        // Extraer el archivo
                        entry.Extract(extractPath, ExtractExistingFileAction.OverwriteSilently);

                        // Actualizar la barra de progreso
                        extractedFiles++;
                        progressBarExtract.Value = (int)((extractedFiles / (double)totalFiles) * 100);
                        // Actualizar el texto del label con el progreso
                        //lblExtract.Text = $"Extrayendo... {extractedFiles}/{totalFiles} archivos";
                        //await Task.Delay(50);

                        // Actualizar el porcentaje de la extracción
                        lblExtract.Text = $"Extrayendo... {Math.Round((extractedFiles / (double)totalFiles) * 100)}% completado";
                        await Task.Delay(10);
                    }

                    lblExtract.Text = "¡Extracción completada!"; // Mensaje final

                    progressBarExtract.Value = 100; // Completar la barra de progreso

                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Error al extraer los archivos: {ex.Message}");
            }
        }
        private string GetVersionFromUpdate(string update)
        {
            return update.Replace("update_", "").Replace(".zip", "");
        }

        private void UpdateConfig(Config config, string latestVersion)
        {
            config.InstalledVersion = latestVersion;
            File.WriteAllText(ConfigFile, JsonConvert.SerializeObject(config));
        }
        public void btnExit_Click(object sender, EventArgs e)
        {
            Application.Exit();
        }

        public void btnStart_Click(object sender, EventArgs e)
        {
            ProcessStartInfo info = new ProcessStartInfo();
            info.FileName = "Nksp.exe";
            info.WorkingDirectory = "bin";
            info.Arguments = "jaslaw62848a86ce7c";
            Process.Start(info);

            Application.Exit();
        }
    }

    // Clases para manejar JSON
    public class Config
    {
        public string InstalledVersion { get; set; }
    }

    public class ServerData
    {
        public string latest_version { get; set; }  // Cambiar de LatestVersion a latest_version
        public string[] updates { get; set; }
    }


}
