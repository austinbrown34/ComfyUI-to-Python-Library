import { api } from "../../scripts/api.js";
import { app } from "../../scripts/app.js";
import { $el } from "../../scripts/ui.js";

const extension = {
    name: "Comfy.SaveAsScript",
    commands: [
        {
            id: "triggerSaveAsScript",
            label: "Save As Script",
            function: () => { extension.savePythonScript(); }
        },
        {
            id: "triggerSaveAsLibrary",
            label: "Save As Library",
            function: () => { extension.saveAsLibrary(); }
        }
    ],
    menuCommands: [
        {
            path: ["File"],
            commands: ["triggerSaveAsScript", "triggerSaveAsLibrary"]
        }
    ],
    init() {
        $el("style", {
            parent: document.head,
        });
    },
    savePythonScript() {
        var filename = prompt("Save script as:");
        if (filename === undefined || filename === null || filename === "") {
            return
        }

        app.graphToPrompt().then(async (p) => {
            const json = JSON.stringify({ name: filename + ".json", workflow: JSON.stringify(p.output, null, 2) }, null, 2); // convert the data to a JSON string
            var response = await api.fetchApi(`/saveasscript`, { method: "POST", body: json });
            if (response.status == 200) {
                const blob = new Blob([await response.text()], { type: "text/python;charset=utf-8" });
                const url = URL.createObjectURL(blob);
                if (!filename.endsWith(".py")) {
                    filename += ".py";
                }

                const a = $el("a", {
                    href: url,
                    download: filename,
                    style: { display: "none" },
                    parent: document.body,
                });
                a.click();
                setTimeout(function () {
                    a.remove();
                    window.URL.revokeObjectURL(url);
                }, 0);
            }
        });
    },
    saveAsLibrary() {
        var name = prompt("Library Name:");
        if (name === undefined || name === null || name === "") {
            return
        }

        app.graphToPrompt().then(async (p) => {
            const json = JSON.stringify({
                name: name,
                workflow: JSON.stringify(p.output, null, 2)
            }, null, 2);

            var response = await api.fetchApi(`/saveaslibrary`, { method: "POST", body: json });
            if (response.status == 200) {
                const blob = new Blob([await response.blob()], { type: "application/zip" });
                const url = URL.createObjectURL(blob);
                if (!name.endsWith(".zip")) {
                    name += ".zip";
                }

                const a = $el("a", {
                    href: url,
                    download: name,
                    style: { display: "none" },
                    parent: document.body,
                });
                a.click();
                setTimeout(function () {
                    a.remove();
                    window.URL.revokeObjectURL(url);
                }, 0);
            } else {
                alert("Error saving library: " + await response.text());
            }
        });
    },
    async setup() {
        console.log("SaveAsScript loaded");
    }
};

app.registerExtension(extension);
