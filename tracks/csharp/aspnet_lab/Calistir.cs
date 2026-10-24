using System;
using System.IO;
using System.Text;
using System.Web.Hosting;
public static class Program {
    public static int Main(string[] a) {
        string app = Path.GetFullPath(a[0]);
        var h = (Barindirici)ApplicationHost.CreateApplicationHost(typeof(Barindirici), "/", app);
        string satir;
        while ((satir = Console.In.ReadLine()) != null) {
            var p = satir.Split('\t');
            string yanit = h.Gonder(p[1], p.Length > 2 ? p[2] : "", p[0], p.Length > 3 ? p[3] : null);
            Console.WriteLine("<<<" + Convert.ToBase64String(Encoding.UTF8.GetBytes(yanit)));
        }
        return 0;
    }
}
