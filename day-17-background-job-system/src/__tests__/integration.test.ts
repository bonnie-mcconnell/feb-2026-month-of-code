import { exec } from "child_process";

test("system boots without crashing", (done) => {
  exec("ts-node src/index.ts", (err) => {
    expect(err).toBeNull();
    done();
  });
});
