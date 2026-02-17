import request from "supertest";
import { app } from "../index";

describe("HTTP Integration", () => {
  it("health endpoint works", async () => {
    const res = await request(app).get("/health");
    expect(res.status).toBe(200);
    expect(res.body.status).toBe("ok");
  });

  it("enqueue endpoint works", async () => {
    const res = await request(app)
      .post("/enqueue")
      .send({ name: "integration-test" });

    expect(res.status).toBe(200);
    expect(res.body.enqueued).toBeDefined();
  });
});
