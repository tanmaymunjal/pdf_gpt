"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [file, setFile] = useState<File>();
  const [tasks, setTasks] = useState([{}]);
  useEffect(() => {
    setTasks([{ task_id: 1, task_status: "Suceeded" }]);
  }, []);

  return (
    <main className="flex flex-col items-center justify-between p-24">
      <form className="mb-8">
        <input
          type="file"
          className="file-input file-input-bordered"
          id="fileInput"
          onChange={(e) => setFile(e.target.files?.[0])}
        />
        <br />
        <br />
        <input type="submit" className="btn btn-info" value="Submit" />
      </form>
      <table className="table table-zebra border border-slate-500">
        <thead>
          <tr className="border border-slate-600">
            <th>Task ID</th>
            <th>Task Status</th>
            <th>Task Result</th>
          </tr>
        </thead>
        <tbody>
          {tasks.map((item, _) => (
            <tr key={item.task_id} className="border border-slate-600">
              <td>{item.task_id}</td>
              <td>{item.task_status}</td>
              <td
                onClick={() => {
                  console.log(1);
                }}
                className="font-medium text-blue-600 underline dark:text-blue-500 hover:no-underline"
              >
                View Task Result
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
