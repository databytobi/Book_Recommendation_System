"use client";

import * as React from "react";
import {
  Controller,
  FormProvider,
  useFormContext,
  type ControllerProps,
  type FieldPath,
  type FieldValues,
} from "react-hook-form";

import { cn } from "@/lib/utils";



const Form = FormProvider;



const FormField = <
  TFieldValues extends FieldValues = FieldValues,
  TName extends FieldPath<TFieldValues> = FieldPath<TFieldValues>
>({
  ...props
}: ControllerProps<TFieldValues, TName>) => {

  return (
    <Controller
      {...props}
    />
  );

};



const FormItemContext =
  React.createContext<{
    id: string;
  }>({
    id: "",
  });



const FormItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(
  (
    {
      className,
      ...props
    },
    ref
  ) => {

    const id =
      React.useId();


    return (

      <FormItemContext.Provider
        value={{
          id,
        }}
      >

        <div
          ref={ref}
          className={cn(
            "space-y-2",
            className
          )}
          {...props}
        />

      </FormItemContext.Provider>

    );

  }
);


FormItem.displayName = "FormItem";



const FormLabel = React.forwardRef<
  HTMLLabelElement,
  React.LabelHTMLAttributes<HTMLLabelElement>
>(
  (
    {
      className,
      ...props
    },
    ref
  ) => {

    return (

      <label
        ref={ref}
        className={cn(
          "text-sm font-medium",
          className
        )}
        {...props}
      />

    );

  }
);


FormLabel.displayName = "FormLabel";



const FormControl = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(
  (
    {
      className,
      ...props
    },
    ref
  ) => {

    return (

      <input
        ref={ref}
        className={cn(
          "flex h-10 w-full rounded-md border px-3 py-2 text-sm",
          className
        )}
        {...props}
      />

    );

  }
);


FormControl.displayName = "FormControl";



function FormMessage() {

  const {
    // FIX: Remove unused formState variable
  } = useFormContext();


  return null;

}



export {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
};