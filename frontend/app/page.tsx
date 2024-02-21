"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File>();
  const [summary, setSummary] = useState<String>("");

  const generateSummary = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!file) return;
    try {
      const data = new FormData();
      data.set("file", file);

      await fetch(process.env.NEXT_PUBLIC_API_HOST + "/generate_summary", {
        method: "POST",
        body: data,
      })
        .then((res) => res.json())
        .then((data) => {
          setSummary(data.summary);
        })
        .catch((e) => {
          throw new Error(e.message);
        });
      // handle the error
    } catch (e: any) {
      // Handle errors here
      console.error(e);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <form onSubmit={generateSummary}>
        <input
          type="file"
          className="file-input file-input-bordered w-full max-w-xs"
          id="fileInput"
          onChange={(e) => setFile(e.target.files?.[0])}
        />
        <br />
        <br />
        <input type="submit" className="btn btn-info" value="Submit" />
      </form>
      {summary != "" && (
        <div>
          <br />
          <br />
          <p> Generated Summary: </p>
          <p> {summary}</p>
        </div>
      )}
    </main>
  );
}
