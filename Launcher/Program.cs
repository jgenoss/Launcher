using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Launcher
{
    internal static class Program
    {
        /// <summary>
        /// Punto de entrada principal para la aplicación.
        /// </summary>
        [STAThread]

        static void Main()
        {

            Process[] procesos = Process.GetProcessesByName("Launcher");

            // Si hay más de una instancia, cerrar todas menos la primera
            if (procesos.Length > 1)
            {
                // Saltamos la primera instancia (la dejamos abierta)
                foreach (Process procesoDuplicado in procesos.Skip(1))
                {
                    procesoDuplicado.Kill();
                }
            }

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new Form1());

        }
    }
}
