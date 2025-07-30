
import sys
import sply

class sp_example:
    def __init__(self,
            mode="",
            show="",
            backend="",
            model_id="",
            seed="",
            temp="",
            num_ctx="",
            ):

        self.res = 0

        self.mode = mode
        sp_args = {}
        sp_args["show"] = show
        sp_args["backend"] = backend
        sp_args["model_id"] = model_id
        sp_args["seed"] = seed
        sp_args["temp"] = temp
        sp_args["num_ctx"] = num_ctx

        for sys_arg in sys.argv[1:]:
            if sys_arg.find("--help") == 0:
                print(f"usage: {sys.argv[0]}"\
                    f" [--help]"\
                    f" [mode=\"plain\"|\"think\" (\"{self.mode}\")]"\
                    f" [show=True|False ({sp_args["show"]})]"\
                    f" [backend=\"backend_id\" (\"{sp_args["backend"]}\")]"\
                    f" [model_id=\"model_id\" (\"{sp_args["model_id"]}\")]"\
                    f" [seed=\"seed\" ({sp_args["seed"]})]"\
                    f" [temp=\"temp\" ({sp_args["temp"]})]"\
                    f" [num_ctx=\"num_ctx\" ({sp_args["num_ctx"]})]"\
                    "")
                self.res = -1
                return
            elif sys_arg.find("mode=") == 0:
                self.mode = sys_arg[5:]
            elif sys_arg.find("show=") == 0:
                self.show = True if sys_arg[5:] == "True" else False
            elif sys_arg.find("backend=") == 0:
                sp_args["backend"] = sys_arg[8:]
            elif sys_arg.find("model_id=") == 0:
                sp_args["model_id"] = sys_arg[9:]
            elif sys_arg.find("seed=") == 0:
                sp_args["seed"] = int(sys_arg[5:])
            elif sys_arg.find("temp=") == 0:
                sp_args["temp"] = float(sys_arg[5:])
            elif sys_arg.find("num_ctx=") == 0:
                sp_args["num_ctx"] = int(sys_arg[8:])

        if self.mode == "plain":
            sp_args["prompt"] = sply.sp.create_prompt_default()
        elif self.mode == "think":
            sp_args["prompt"] = sply.sp.create_prompt_think()

        self.sp = sply.sp(**sp_args)

        if self.mode == "plain":
            self.runcode = self.sp.runcode
        elif self.mode == "think":
            self.runcode = self.sp.runcode_think

