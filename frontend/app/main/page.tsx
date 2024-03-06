"use client";
import { use, useEffect, useState } from "react";

export default function Home() {
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File>();
  const [tasks, setTasks] = useState<Array<Object>>([]);
  const [summary, setSummary] = useState<string>("");
  useEffect(() => {
    refresh();
  }, []);

  function convertToTaskList(jsonArray: Array<object>) {
    const succeededTasks: Array<object> = [];
    const otherTasks: Array<Object> = [];
    jsonArray.forEach((obj) => {
      const task = {
        task_id: obj.user_task_id,
        task_status: obj.user_task_status || "Unknown", // If user_task_status is not present, default to "Unknown"
      };
      if (obj.user_task_status === "SUCCESS") {
        succeededTasks.push(task);
      } else {
        otherTasks.push(task);
      }
    });
    return succeededTasks.concat(otherTasks);
  }

  async function submitJob(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const jwt_token = localStorage.getItem("jwt_token");
    console.log(jwt_token);
    if (!file) return;
    try {
      const data = new FormData();
      data.set("file", file);

      await fetch(
        process.env.NEXT_PUBLIC_API_HOST +
          "/generate_summary?token=" +
          jwt_token,
        {
          method: "POST",
          body: data,
        },
      ).then((res) => {
        if (res.status != 200) {
          setError("There was an internal server error,please try later!");
        } else {
          res.json().then((data) => {
            let val = { task_id: data.task_id, task_status: "Pending" };
            console.log(tasks);
            setTasks([...tasks, val]);
          });
        }
      });
    } catch (e: any) {
      setError(e.toString());
    }
  }

  async function fetchData(task_id: string) {
    const jwt_token = localStorage.getItem("jwt_token");
    try {
      await fetch(
        process.env.NEXT_PUBLIC_API_HOST +
          "/user/get_summary?token=" +
          jwt_token +
          "&task_id=" +
          task_id,
        {
          method: "GET",
        },
      ).then((res) => {
        if (res.status != 200) {
          setError("There was an internal server error,please try later!");
        } else {
          res.json().then((data) => {
            console.log(data);
            setSummary(data.result);
          });
        }
      });
    } catch (e: any) {
      setError(e);
    }
  }

  async function refresh() {
    const jwt_token = localStorage.getItem("jwt_token");
    try {
      await fetch(
        process.env.NEXT_PUBLIC_API_HOST + "/user/tasks?token=" + jwt_token,
        {
          method: "GET",
        },
      ).then((res) => {
        if (res.status != 200) {
          setError("There was an internal server error,please try later!");
        } else {
          res.json().then((data) => {
            setTasks(convertToTaskList(data.tasks));
          });
        }
      });
    } catch (e: any) {
      setError(e);
    }
  }

  return (
    <main className="flex flex-col items-center justify-between p-24">
      <form className="mb-8" onSubmit={submitJob}>
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
      {error && (
        <div
          role="alert"
          className="alert alert-error shrink w-auto h-14 mx-auto mt-2"
          onClick={() => {
            setError(null);
          }}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="stroke-current shrink-0 h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{error}</span>
        </div>
      )}
      {tasks.length != 0 && (
        <div>
          <button
            onClick={refresh}
            className="flex items-center px-4 py-2 my-3 font-medium tracking-wide text-white capitalize transition-colors duration-300 transform bg-indigo-600 rounded-lg hover:bg-indigo-500 focus:outline-none focus:ring focus:ring-indigo-300 focus:ring-opacity-80 ml-auto"
          >
            <svg
              className="w-5 h-5 mx-1"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path
                fillRule="evenodd"
                d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z"
                clipRule="evenodd"
              />
            </svg>
            <span className="mx-1">Refresh</span>
          </button>
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
                  <td>
                    <button
                      onClick={() => {
                        if (item.task_status != "SUCCESS") {
                          setError("Task not completed yet");
                        } else {
                          fetchData(item.task_id);
                        }
                      }}
                      className="font-medium text-blue-600 underline dark:text-blue-500 hover:no-underline"
                    >
                      View Task Result
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {summary.length != 0 && (
        <div>
          <div className="card w-96 bg-base-100 shadow-xl mt-5">
            <div className="card-body">
              <h2 className="card-title">Generated summary!</h2>
              <p>{summary}</p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
